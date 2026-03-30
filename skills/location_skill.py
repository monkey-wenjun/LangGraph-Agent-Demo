"""
Location Skill - GPS 定位服务
获取设备当前位置信息，支持 IP 定位、GPS 坐标获取
"""

import json
import urllib.request
from typing import List, Optional
from langchain_core.tools import tool, BaseTool
from .base import Skill


class LocationSkill(Skill):
    """位置定位 Skill"""

    @property
    def name(self) -> str:
        return "location"

    @property
    def description(self) -> str:
        return "获取当前设备的 GPS 位置信息，支持 IP 定位、坐标获取和地址解析"

    def get_tools(self) -> List[BaseTool]:
        return [
            get_current_location,     # 获取当前位置
            get_location_by_ip,       # IP 定位
            get_gps_coordinates,      # 获取 GPS 坐标
            parse_address_from_coords # 从坐标解析地址
        ]


@tool
def get_current_location() -> str:
    """
    获取当前设备的地理位置信息
    优先使用 GPS，如果不支持则使用 IP 定位
    
    返回当前位置的经纬度坐标和城市信息
    """
    # 尝试 IP 定位
    try:
        # 使用 ip-api 获取 IP 位置
        req = urllib.request.Request(
            "http://ip-api.com/json/?lang=zh-CN",
            headers={"User-Agent": "LangGraph-Agent/1.0"},
            method='GET'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("status") == "success":
            lat = data.get("lat", 0)
            lon = data.get("lon", 0)
            city = data.get("city", "")
            region = data.get("regionName", "")
            country = data.get("country", "")
            
            return f"📍 当前位置信息：\n\n坐标: {lon},{lat}\n城市: {country} {region} {city}\n\n💡 提示：这是基于 IP 的大致位置，如需精确位置请使用 GPS 设备。"
        else:
            return "❌ 位置获取失败"
    except Exception as e:
        return f"❌ 无法获取位置: {str(e)}\n\n请手动提供位置信息，例如：\n- 城市名称：北京、上海、广州等\n- 具体地址：北京市朝阳区望京街道\n- 经纬度坐标：116.397428,39.90923"


@tool
def get_location_by_ip() -> str:
    """
    通过 IP 地址获取当前设备的大致位置
    """
    return get_current_location()


@tool
def get_gps_coordinates() -> str:
    """
    获取当前 GPS 坐标
    
    注意：此功能需要在支持 GPS 的设备上运行（如手机、带有 GPS 模块的电脑）
    在 Web 环境中需要用户授权获取位置权限
    """
    # 由于 Python 脚本运行在服务器端，无法直接获取客户端 GPS
    # 这里返回提示信息
    return """📱 GPS 坐标获取说明：

由于当前运行在服务器环境，无法直接获取设备 GPS 坐标。

**请通过以下方式提供您的位置：**

1. **手动输入坐标**
   格式：经度,纬度
   例如：116.397428,39.90923（北京天安门）
   例如：121.4737,31.2304（上海人民广场）

2. **提供城市或地址**
   例如：我在北京
   例如：上海市浦东新区陆家嘴

3. **使用 IP 定位（已自动获取）**
   我可以尝试通过 IP 获取您的大致位置

**常见城市坐标参考：**
• 北京天安门：116.397428,39.90923
• 上海人民广场：121.4737,31.2304
• 广州塔：113.3245,23.1064
• 深圳市民中心：114.0579,22.5431
• 成都天府广场：104.0665,30.5723

请告诉我您的位置，我可以为您推荐附近的麦当劳餐厅！"""


@tool
def parse_address_from_coords(longitude: float, latitude: float) -> str:
    """
    从经纬度坐标解析地址信息
    
    Args:
        longitude: 经度，例如 116.397428
        latitude: 纬度，例如 39.90923
    """
    # 这里会返回高德格式的坐标，方便后续调用高德 API
    return f"坐标 {longitude},{latitude} 已记录。如需详细地址解析，请使用 gaode 技能的 regeocode 工具。"
