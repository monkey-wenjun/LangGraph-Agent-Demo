"""
Skill 选择器 - 根据用户输入智能选择最合适的 Skill
"""

import os
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import BaseTool

# API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

if OPENAI_API_KEY:
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0.1)
elif DEEPSEEK_API_KEY:
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.1
    )
else:
    raise ValueError("请设置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY 环境变量")


class SkillSelector:
    """Skill 选择器，基于用户输入选择最合适的 Skill"""
    
    def __init__(self, skills: List[Any]):
        self.skills = skills
        self.skill_docs = self._build_skill_docs()
    
    def _build_skill_docs(self) -> str:
        """构建所有 Skill 的文档摘要"""
        docs = ["# 可用技能列表\n"]
        
        for skill in self.skills:
            doc = skill.get_documentation()
            if doc:
                # 提取文档的前几行作为描述
                lines = doc.split('\n')
                desc = ""
                for line in lines:
                    if line.startswith('# ') or line.startswith('## 描述'):
                        continue
                    if line.strip() and not line.startswith('##'):
                        desc = line.strip()
                        break
                
                docs.append(f"## {skill.name}\n")
                docs.append(f"描述: {skill.description}\n")
                docs.append(f"工具: {', '.join([t.name for t in skill.get_tools()])}\n")
                if desc:
                    docs.append(f"详细: {desc}\n")
            else:
                docs.append(f"## {skill.name}\n")
                docs.append(f"描述: {skill.description}\n")
                docs.append(f"工具: {', '.join([t.name for t in skill.get_tools()])}\n")
            docs.append("\n")
        
        return '\n'.join(docs)
    
    def select_skills(self, user_input: str) -> List[str]:
        """
        根据用户输入选择应该激活的 Skills
        返回 Skill 名称列表
        """
        system_prompt = f"""你是一个智能 Skill 选择器。根据用户的输入，判断需要激活哪些技能来处理请求。

{self.skill_docs}

选择规则：
1. 分析用户的意图和需求
2. 选择最相关的技能（可以选择多个）
3. 如果用户只是闲聊或问候，不需要激活任何技能
4. 只返回技能名称列表，用逗号分隔
5. 如果没有匹配的技能，返回 "none"

输出格式：只返回技能名称，例如：cli,file 或 cli 或 none"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"用户输入: {user_input}")
        ]
        
        try:
            response = llm.invoke(messages)
            result = response.content.strip().lower()
            
            if result == "none" or not result:
                return []
            
            # 解析返回的技能名称
            selected = [s.strip() for s in result.split(',') if s.strip()]
            
            # 验证技能名称是否有效
            valid_skills = [s.name for s in self.skills]
            selected = [s for s in selected if s in valid_skills]
            
            return selected
        except Exception as e:
            print(f"[SkillSelector] 选择技能失败: {e}")
            return []
    
    def get_tools_for_skills(self, skill_names: List[str]) -> List[BaseTool]:
        """获取指定 Skills 的所有 Tools"""
        tools = []
        for skill in self.skills:
            if skill.name in skill_names:
                tools.extend(skill.get_tools())
        return tools
    
    def get_all_tools(self) -> List[BaseTool]:
        """获取所有 Skills 的 Tools"""
        tools = []
        for skill in self.skills:
            tools.extend(skill.get_tools())
        return tools
