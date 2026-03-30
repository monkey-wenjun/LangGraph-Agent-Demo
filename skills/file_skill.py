"""
File Skill - 操作本地文件的命令脚本
支持读取、写入、列出目录内容
"""

import os
from typing import List
from langchain_core.tools import tool, BaseTool
from .base import Skill

# 允许操作的基础目录（当前工作目录）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _sanitize_path(path: str) -> str:
    """将路径限制在 BASE_DIR 内，防止目录遍历"""
    # 先解析为绝对路径（如果是相对路径，基于 BASE_DIR）
    if not os.path.isabs(path):
        path = os.path.join(BASE_DIR, path)
    resolved = os.path.abspath(path)
    # 确保在 BASE_DIR 下
    if not resolved.startswith(BASE_DIR + os.sep) and resolved != BASE_DIR:
        raise ValueError(f"路径越界: {path}")
    return resolved


class FileSkill(Skill):
    """本地文件操作 Skill"""

    @property
    def name(self) -> str:
        return "file"

    @property
    def description(self) -> str:
        return "安全地读取、写入、列出项目目录下的文件"

    def get_tools(self) -> List[BaseTool]:
        return [read_file, write_file, list_dir]


@tool
def read_file(path: str) -> str:
    """
    读取指定路径的文本文件内容

    Args:
        path: 文件路径（相对项目根目录或绝对路径）
    """
    try:
        target = _sanitize_path(path)
        if not os.path.isfile(target):
            return f"错误：文件不存在: {target}"
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        return f"【{target}】内容:\n```\n{content}\n```"
    except ValueError as e:
        return f"错误: {e}"
    except Exception as e:
        return f"读取文件失败: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """
    将内容写入指定路径的文本文件（覆盖写入）

    Args:
        path: 文件路径（相对项目根目录或绝对路径）
        content: 要写入的文本内容
    """
    try:
        target = _sanitize_path(path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return f"成功写入文件: {target}"
    except ValueError as e:
        return f"错误: {e}"
    except Exception as e:
        return f"写入文件失败: {e}"


@tool
def list_dir(path: str = ".") -> str:
    """
    列出指定目录下的文件和子目录

    Args:
        path: 目录路径（相对项目根目录或绝对路径），默认为当前目录
    """
    try:
        target = _sanitize_path(path)
        if not os.path.isdir(target):
            return f"错误：目录不存在: {target}"
        items = os.listdir(target)
        if not items:
            return f"目录 {target} 为空"
        lines = [f"📁 {target} 内容:"]
        for item in sorted(items):
            full = os.path.join(target, item)
            prefix = "📂" if os.path.isdir(full) else "📄"
            lines.append(f"  {prefix} {item}")
        return "\n".join(lines)
    except ValueError as e:
        return f"错误: {e}"
    except Exception as e:
        return f"列出目录失败: {e}"
