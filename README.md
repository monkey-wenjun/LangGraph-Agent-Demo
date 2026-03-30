# LangGraph Agent Demo

基于 LangGraph 构建的智能 Agent 系统，支持文档驱动的 Skill 自动发现、智能 Skill 选择和记忆存储。

## 功能特性

- ✅ **文档驱动的 Skill 系统** - 每个 Skill 都有 Markdown 文档，AI 根据文档理解技能能力
- ✅ **智能 Skill 选择** - 根据用户输入自动选择最合适的 Skills
- ✅ **Skill 自动发现** - 自动加载 `skills/` 目录下的功能模块
- ✅ **记忆存储** - 使用 `MemorySaver` 保存对话状态，支持多会话隔离
- ✅ **本地命令执行** - 通过 CLI Skill 安全执行系统命令
- ✅ **文件操作** - 支持读取、写入、列出项目目录下的文件
- ✅ **麦当劳服务** - 基于 FastMCP 的麦当劳点餐助手
- ✅ **Web 聊天界面** - 基于 FastAPI + 原生 HTML/JS

## 项目结构

```
agent_web_chat/
├── agent.py                  # LangGraph Agent 核心
├── main.py                   # FastAPI Web 服务
├── mcdonalds_mcp_server.py   # FastMCP 麦当劳服务器（可独立运行）
├── skills/
│   ├── base.py               # Skill 基类
│   ├── __init__.py           # 自动发现所有 skills
│   ├── skill_selector.py     # Skill 选择器
│   ├── cli_skill.py          # dig 命令查询
│   ├── file_skill.py         # 本地文件操作
│   ├── mcdonalds_skill.py    # 麦当劳服务
│   └── docs/                 # Skill 文档目录
│       ├── cli_skill.md
│       ├── file_skill.md
│       └── mcdonalds_skill.md
├── templates/
│   └── index.html            # 聊天页面
├── static/
│   └── style.css             # 样式
├── .env.example              # 环境变量模板
└── requirements.txt          # 依赖列表
```

## 快速开始

### 1. 安装依赖

```bash
pip install langgraph langchain langchain-openai fastapi uvicorn jinja2 python-multipart fastmcp
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 3. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. 访问界面

打开浏览器访问 `http://localhost:8000`

## 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 是（或 OPENAI_API_KEY） |
| `OPENAI_API_KEY` | OpenAI API Key | 否 |

## 使用示例

### 查询域名解析
```
用户: 查询 example.com 的 A 记录
系统: 🤖 选择 skills: ['cli']
AI: example.com 的 A 记录有两个 IP 地址...
```

### 麦当劳点餐
```
用户: 我想吃麦当劳，看看有什么汉堡
系统: 🤖 选择 skills: ['mcdonalds']
AI: 🍔 汉堡菜单：巨无霸(¥25.5)、麦辣鸡腿汉堡(¥22.0)...
```

### 营养计算
```
用户: 巨无霸、薯条(大)、可乐(中)的热量是多少
系统: 🤖 选择 skills: ['mcdonalds']
AI: 🔥 热量: 1230 千卡...
```

## 添加新 Skill

1. 在 `skills/` 目录创建 `{name}_skill.py`
2. 在 `skills/docs/` 创建 `{name}_skill.md` 文档
3. 继承 `Skill` 基类实现 `name`、`description`、`get_tools()`
4. 重启服务，自动加载

## FastMCP 麦当劳服务器

麦当劳服务也可以独立作为 MCP 服务器运行：

```bash
# stdio 模式
python mcdonalds_mcp_server.py

# HTTP 模式
python mcdonalds_mcp_server.py --transport http --port 8001
```

## 技术栈

- [LangGraph](https://langchain-ai.github.io/langgraph/) - 构建有状态的 AI 工作流
- [LangChain](https://python.langchain.com/) - LLM 应用开发框架
- [FastMCP](https://github.com/prefecthq/fastmcp) - MCP 服务器框架
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Web 框架

## 许可证

MIT License
