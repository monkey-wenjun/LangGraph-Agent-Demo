"""
Skill 基类定义 - 支持文档驱动
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_core.tools import BaseTool


class Skill(ABC):
    """Skill 基类，所有 skill 必须继承并实现以下方法"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Skill 名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Skill 描述"""
        pass

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """返回该 skill 提供的工具列表"""
        pass

    def get_documentation(self) -> Optional[str]:
        """
        返回 Skill 的文档内容
        默认从 docs/{skill_name}.md 读取
        """
        docs_dir = os.path.join(os.path.dirname(__file__), "docs")
        doc_file = os.path.join(docs_dir, f"{self.name}_skill.md")
        
        if os.path.exists(doc_file):
            with open(doc_file, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def get_metadata(self) -> Dict[str, Any]:
        """返回 Skill 的元数据信息"""
        return {
            "name": self.name,
            "description": self.description,
            "tools": [tool.name for tool in self.get_tools()],
            "has_documentation": self.get_documentation() is not None
        }
