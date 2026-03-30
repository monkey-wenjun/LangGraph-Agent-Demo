"""
CLI Skill - 支持执行安全的本地命令
目前支持 dig 查询域名解析
"""

import subprocess
import shutil
from typing import List
from langchain_core.tools import tool, BaseTool
from .base import Skill


class CliSkill(Skill):
    """命令行工具 Skill"""

    @property
    def name(self) -> str:
        return "cli"

    @property
    def description(self) -> str:
        return "执行安全的本地命令行工具，如 dig 查询域名解析"

    def get_tools(self) -> List[BaseTool]:
        return [dig_query]


@tool
def dig_query(domain: str, record_type: str = "A") -> str:
    """
    使用 dig 命令查询域名的 DNS 解析记录

    Args:
        domain: 要查询的域名，例如 "example.com"
        record_type: DNS 记录类型，例如 "A", "AAAA", "MX", "NS", "TXT", "CNAME"
    """
    if not shutil.which("dig"):
        return "错误：当前系统未安装 dig 命令，请安装 bind-utils 或 dnsutils 包。"

    # 安全校验：只允许字母、数字、点、横线、下划线
    safe_domain = "".join(c for c in domain if c.isalnum() or c in ".-_")
    safe_record = "".join(c for c in record_type if c.isalnum())

    if not safe_domain:
        return "错误：域名格式不合法"

    try:
        result = subprocess.run(
            ["dig", safe_domain, safe_record, "+short"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        output = result.stdout.strip()
        if result.returncode != 0:
            return f"dig 执行失败: {result.stderr.strip()}"
        if not output:
            return f"未查询到 {safe_domain} 的 {safe_record} 记录（或返回为空）。"
        return f"dig {safe_domain} {safe_record} 查询结果:\n{output}"
    except subprocess.TimeoutExpired:
        return "错误：dig 命令执行超时"
    except Exception as e:
        return f"错误：执行 dig 时发生异常: {e}"
