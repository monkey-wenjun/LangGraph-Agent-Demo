"""
LangGraph Agent 核心 - 支持动态 Skill 选择和记忆存储
"""

import os
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from skills import discover_skills
from skills.skill_selector import SkillSelector


# API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

if OPENAI_API_KEY:
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.2)
elif DEEPSEEK_API_KEY:
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.2
    )
else:
    raise ValueError("请设置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY 环境变量")


# ========== 定义状态 ==========
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    active_skills: List[str]  # 当前激活的 skills
    skill_calls: List[Dict[str, Any]]  # 记录 skill 调用历史


# ========== 加载 Skills ==========
all_skills = discover_skills()
skill_selector = SkillSelector(all_skills)
print(f"[agent] 共加载 {len(all_skills)} 个 skills: {[s.name for s in all_skills]}")


# ========== 定义节点 ==========
def skill_selection_node(state: AgentState) -> dict:
    """Skill 选择节点：根据用户输入选择需要激活的 Skills"""
    messages = state["messages"]
    
    # 获取最后一条用户消息
    last_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_message = msg
            break
    
    if not last_message:
        return {"active_skills": [], "skill_calls": []}
    
    user_input = last_message.content
    
    # 使用 SkillSelector 选择 Skills
    selected_skills = skill_selector.select_skills(user_input)
    
    if selected_skills:
        print(f"[agent] 选择的 skills: {selected_skills}")
    
    return {
        "active_skills": selected_skills,
        "skill_calls": [{"event": "skill_selection", "skills": selected_skills}]
    }


def chatbot_node(state: AgentState) -> dict:
    """聊天节点：调用 LLM，可能触发工具调用"""
    active_skills = state.get("active_skills", [])
    
    # 获取当前激活 skills 的 tools
    if active_skills:
        tools = skill_selector.get_tools_for_skills(active_skills)
    else:
        # 如果没有选择特定 skill，使用所有 tools
        tools = skill_selector.get_all_tools()
    
    # 绑定 tools 到 LLM
    llm_with_tools = llm.bind_tools(tools)
    
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def tools_node(state: AgentState) -> dict:
    """工具执行节点：执行 Skill 工具并记录调用信息"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 获取工具调用信息
    tool_calls = getattr(last_message, 'tool_calls', [])
    
    skill_calls = state.get("skill_calls", [])
    
    # 执行工具
    active_skills = state.get("active_skills", [])
    if active_skills:
        tools = skill_selector.get_tools_for_skills(active_skills)
    else:
        tools = skill_selector.get_all_tools()
    
    # 创建 ToolNode 并执行
    tool_node = ToolNode(tools=tools)
    result = tool_node.invoke(state)
    
    # 记录工具调用
    for tool_call in tool_calls:
        skill_calls.append({
            "event": "tool_call",
            "tool": tool_call.get('name', 'unknown'),
            "arguments": tool_call.get('args', {})
        })
    
    result["skill_calls"] = skill_calls
    return result


# ========== 构建图 ==========
builder = StateGraph(AgentState)

# 添加节点
builder.add_node("skill_selection", skill_selection_node)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", tools_node)

# 添加边
builder.add_edge(START, "skill_selection")
builder.add_edge("skill_selection", "chatbot")

# 条件边：如果 LLM 要调用工具，就去 tools 节点
builder.add_conditional_edges(
    "chatbot",
    tools_condition,
    {"tools": "tools", END: END}
)

# 工具执行完后返回 chatbot
builder.add_edge("tools", "chatbot")

# 记忆存储
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


def run_agent(user_input: str, thread_id: str = "default") -> dict:
    """
    运行 Agent，返回包含回复和技能调用信息的字典
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    result = graph.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "active_skills": [],
            "skill_calls": []
        },
        config=config
    )
    
    # 提取最后一条 AI 消息
    ai_message = None
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage):
            ai_message = msg
            break
    
    return {
        "reply": ai_message.content if ai_message else "（无回复）",
        "active_skills": result.get("active_skills", []),
        "skill_calls": result.get("skill_calls", [])
    }


def stream_agent(user_input: str, thread_id: str = "default"):
    """
    流式运行 Agent，yield 每个事件
    包含技能选择、工具调用等信息
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    for event in graph.stream(
        {
            "messages": [HumanMessage(content=user_input)],
            "active_skills": [],
            "skill_calls": []
        },
        config=config,
        stream_mode="values"
    ):
        yield event


if __name__ == "__main__":
    print("🤖 Agent 测试模式 (输入 'quit' 退出)\n")
    config = {"configurable": {"thread_id": "test-session"}}
    
    while True:
        user_input = input("你: ").strip()
        if user_input.lower() in ["quit", "exit", "退出"]:
            print("👋 再见!")
            break
        
        result = run_agent(user_input, thread_id="test-session")
        print(f"🤖 AI: {result['reply']}")
        if result['active_skills']:
            print(f"   [使用技能: {', '.join(result['active_skills'])}]")
        print()
