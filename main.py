"""
FastAPI Web 服务
提供聊天页面和 /chat API - 支持技能调用展示
"""

import os
import uuid
import json
from typing import List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from agent import run_agent, stream_agent
from langchain_core.messages import AIMessage, ToolMessage

# 确保工作目录正确
os.chdir(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="LangGraph Agent Web Chat - 智能 Skill 选择")

# 静态资源
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    thread_id: str
    active_skills: List[str]
    skill_calls: List[Dict[str, Any]]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"request": request})


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """聊天接口 - 返回完整响应包含技能调用信息"""
    thread_id = req.thread_id or str(uuid.uuid4())
    result = run_agent(req.message, thread_id=thread_id)
    
    return ChatResponse(
        reply=result["reply"],
        thread_id=thread_id,
        active_skills=result.get("active_skills", []),
        skill_calls=result.get("skill_calls", [])
    )


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """流式聊天接口 - Server-Sent Events"""
    thread_id = req.thread_id or str(uuid.uuid4())
    
    async def event_generator():
        for event in stream_agent(req.message, thread_id=thread_id):
            # 提取消息和技能调用信息
            messages = event.get("messages", [])
            active_skills = event.get("active_skills", [])
            skill_calls = event.get("skill_calls", [])
            
            # 构建响应数据
            data = {
                "thread_id": thread_id,
                "active_skills": active_skills,
                "skill_calls": skill_calls,
                "messages": []
            }
            
            # 处理消息
            for msg in messages:
                if isinstance(msg, AIMessage):
                    data["messages"].append({
                        "role": "assistant",
                        "content": msg.content,
                        "tool_calls": getattr(msg, 'tool_calls', None)
                    })
                elif isinstance(msg, ToolMessage):
                    data["messages"].append({
                        "role": "tool",
                        "content": msg.content,
                        "tool": msg.name if hasattr(msg, 'name') else 'unknown'
                    })
            
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.get("/api/skills")
async def get_skills():
    """获取所有可用技能列表"""
    from agent import all_skills
    
    skills_info = []
    for skill in all_skills:
        skills_info.append({
            "name": skill.name,
            "description": skill.description,
            "tools": [t.name for t in skill.get_tools()],
            "documentation": skill.get_documentation() is not None
        })
    
    return {"skills": skills_info}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
