"""
Skill 自动发现与注册
自动加载 skills 目录下所有以 _skill.py 结尾的模块
"""

import os
import importlib
import inspect
from typing import List
from langchain_core.tools import BaseTool
from .base import Skill


def discover_skills() -> List[Skill]:
    """自动发现并实例化所有 skill"""
    skills = []
    current_dir = os.path.dirname(os.path.abspath(__file__))

    for filename in sorted(os.listdir(current_dir)):
        if filename.endswith("_skill.py"):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"." + module_name, package=__name__)
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, Skill)
                        and obj is not Skill
                        and not inspect.isabstract(obj)
                    ):
                        instance = obj()
                        skills.append(instance)
                        print(f"[skills] 已加载: {instance.name}")
            except Exception as e:
                print(f"[skills] 加载 {module_name} 失败: {e}")

    return skills


def get_all_tools() -> List[BaseTool]:
    """获取所有 skill 提供的 tools"""
    tools = []
    for skill in discover_skills():
        tools.extend(skill.get_tools())
    return tools


# 向后兼容
__all__ = ['Skill', 'discover_skills', 'get_all_tools']
