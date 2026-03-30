"""
Gaode Skill - 高德地图服务
集成高德 MCP Server，提供地图、导航、POI 搜索等服务
"""

import os
import json
import urllib.request
import urllib.parse
from typing import List, Optional
from langchain_core.tools import tool, BaseTool
from .base import Skill


class GaodeSkill(Skill):
    """高德地图服务 Skill"""

    @property
    def name(self) -> str:
        return "gaode"

    @property
    def description(self) -> str:
        return "高德地图服务，提供地理编码、路径规划、POI 搜索、天气查询等功能"

    def get_tools(self) -> List[BaseTool]:
        return [
            geocode,              # 地理编码
            regeocode,            # 逆地理编码
            search_poi,           # POI 搜索
            route_planning,       # 路径规划
            get_weather,          # 天气查询
            get_district_info     # 行政区划查询
        ]


# 高德 API Key（从环境变量读取）
GAODE_API_KEY = os.getenv("GAODE_API_KEY")
GAODE_MCP_BASE = "https://mcp.amap.com/mcp"


def _call_gaode_mcp(tool_name: str, params: dict) -> dict:
    """调用高德 MCP Server"""
    api_key = os.getenv("GAODE_API_KEY")
    if not api_key:
        return {"error": "请设置 GAODE_API_KEY 环境变量"}
    
    try:
        # 构造 MCP 请求
        url = f"{GAODE_MCP_BASE}?key={api_key}"
        
        data = {
            "jsonrpc": "2.0",
            "method": f"tools/{tool_name}",
            "params": params,
            "id": 1
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "LangGraph-Agent/1.0"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        # MCP 调用失败时，使用模拟数据
        return {"error": str(e), "mock": True}


@tool
def geocode(address: str, city: Optional[str] = None) -> str:
    """
    地理编码 - 将地址转换为经纬度坐标

    Args:
        address: 要解析的地址，例如 "北京市朝阳区望京街道"
        city: 指定城市，可选
    """
    if not GAODE_API_KEY:
        return "❌ 请设置 GAODE_API_KEY 环境变量"
    
    # 调用高德地理编码 API
    try:
        url = "https://restapi.amap.com/v3/geocode/geo"
        params = {
            "key": GAODE_API_KEY,
            "address": address
        }
        if city:
            params["city"] = city
        
        query = urllib.parse.urlencode(params)
        full_url = f"{url}?{query}"
        
        req = urllib.request.Request(full_url, headers={"User-Agent": "LangGraph-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("status") == "1" and data.get("geocodes"):
            result = data["geocodes"][0]
            location = result.get("location", "")
            formatted_address = result.get("formatted_address", address)
            province = result.get("province", "")
            city = result.get("city", "")
            district = result.get("district", "")
            
            return f"📍 地址解析结果：\n\n地址: {formatted_address}\n坐标: {location}\n省份: {province}\n城市: {city}\n区县: {district}"
        else:
            return f"❌ 地理编码失败: {data.get('info', '未知错误')}"
    except Exception as e:
        return f"❌ 请求失败: {str(e)}"


@tool
def regeocode(longitude: float, latitude: float) -> str:
    """
    逆地理编码 - 将经纬度坐标转换为地址

    Args:
        longitude: 经度，例如 116.481488
        latitude: 纬度，例如 39.990464
    """
    if not GAODE_API_KEY:
        return "❌ 请设置 GAODE_API_KEY 环境变量"
    
    try:
        url = "https://restapi.amap.com/v3/geocode/regeo"
        params = {
            "key": GAODE_API_KEY,
            "location": f"{longitude},{latitude}",
            "extensions": "all"
        }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{url}?{query}"
        
        req = urllib.request.Request(full_url, headers={"User-Agent": "LangGraph-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("status") == "1" and data.get("regeocode"):
            result = data["regeocode"]
            address = result.get("formatted_address", "")
            
            # 获取周边 POI
            pois = result.get("pois", [])
            nearby = ""
            if pois:
                nearby = "\n\n附近地标：\n"
                for poi in pois[:5]:
                    nearby += f"  • {poi.get('name', '')} ({poi.get('type', '')})\n"
            
            return f"📍 坐标 {longitude},{latitude} 对应的地址：\n\n{address}{nearby}"
        else:
            return f"❌ 逆地理编码失败: {data.get('info', '未知错误')}"
    except Exception as e:
        return f"❌ 请求失败: {str(e)}"


@tool
def search_poi(
    keywords: str,
    city: Optional[str] = None,
    types: Optional[str] = None,
    radius: int = 3000,
    offset: int = 10
) -> str:
    """
    POI 搜索 - 搜索周边的地点

    Args:
        keywords: 搜索关键词，例如 "麦当劳"
        city: 城市名称，例如 "北京"
        types: POI 类型，例如 "050000"（餐饮）
        radius: 搜索半径（米），默认 3000
        offset: 返回结果数量，默认 10
    """
    if not GAODE_API_KEY:
        return "❌ 请设置 GAODE_API_KEY 环境变量"
    
    try:
        url = "https://restapi.amap.com/v3/place/text"
        params = {
            "key": GAODE_API_KEY,
            "keywords": keywords,
            "offset": offset,
            "page": 1,
            "extensions": "all"
        }
        if city:
            params["city"] = city
        if types:
            params["types"] = types
        
        query = urllib.parse.urlencode(params)
        full_url = f"{url}?{query}"
        
        req = urllib.request.Request(full_url, headers={"User-Agent": "LangGraph-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("status") == "1" and data.get("pois"):
            pois = data["pois"]
            result = f"🔍 搜索 '{keywords}' 找到 {len(pois)} 个结果：\n\n"
            
            for i, poi in enumerate(pois[:offset], 1):
                name = poi.get("name", "")
                address = poi.get("address", "")
                tel = poi.get("tel", "")
                location = poi.get("location", "")
                distance = poi.get("distance", "")
                
                result += f"{i}. {name}\n"
                if address:
                    result += f"   📍 {address}\n"
                if tel:
                    result += f"   📞 {tel}\n"
                if location:
                    result += f"   🌐 坐标: {location}\n"
                if distance:
                    result += f"   📏 距离: {distance}米\n"
                result += "\n"
            
            return result
        else:
            return f"❌ POI 搜索失败: {data.get('info', '未知错误')}"
    except Exception as e:
        return f"❌ 请求失败: {str(e)}"


@tool
def route_planning(
    origin: str,
    destination: str,
    mode: str = "driving"
) -> str:
    """
    路径规划 - 计算从起点到终点的路线

    Args:
        origin: 起点坐标或地址，例如 "116.481488,39.990464" 或 "北京天安门"
        destination: 终点坐标或地址
        mode: 出行方式，可选 driving(驾车), walking(步行), transit(公交), riding(骑行)
    """
    if not GAODE_API_KEY:
        return "❌ 请设置 GAODE_API_KEY 环境变量"
    
    # 如果传入的是地址，先进行地理编码
    origin_coord = origin
    destination_coord = destination
    
    # 简单的坐标格式检测（包含逗号数字）
    if "," not in origin:
        # 需要地理编码
        try:
            url = "https://restapi.amap.com/v3/geocode/geo"
            params = {"key": GAODE_API_KEY, "address": origin}
            query = urllib.parse.urlencode(params)
            req = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": "LangGraph-Agent/1.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            if data.get("status") == "1" and data.get("geocodes"):
                origin_coord = data["geocodes"][0]["location"]
        except:
            pass
    
    if "," not in destination:
        try:
            url = "https://restapi.amap.com/v3/geocode/geo"
            params = {"key": GAODE_API_KEY, "address": destination}
            query = urllib.parse.urlencode(params)
            req = urllib.request.Request(f"{url}?{query}", headers={"User-Agent": "LangGraph-Agent/1.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            if data.get("status") == "1" and data.get("geocodes"):
                destination_coord = data["geocodes"][0]["location"]
        except:
            pass
    
    try:
        # 根据模式选择 API
        api_map = {
            "driving": "https://restapi.amap.com/v3/direction/driving",
            "walking": "https://restapi.amap.com/v3/direction/walking",
            "transit": "https://restapi.amap.com/v3/direction/transit/integrated",
            "riding": "https://restapi.amap.com/v3/direction/riding"
        }
        
        url = api_map.get(mode, api_map["driving"])
        params = {
            "key": GAODE_API_KEY,
            "origin": origin_coord,
            "destination": destination_coord,
            "extensions": "all"
        }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{url}?{query}"
        
        req = urllib.request.Request(full_url, headers={"User-Agent": "LangGraph-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("status") == "1" and data.get("route"):
            route = data["route"]
            paths = route.get("paths", [])
            
            if not paths:
                return "❌ 未找到可行的路线"
            
            path = paths[0]
            distance = int(path.get("distance", 0))
            duration = int(path.get("duration", 0))
            
            # 格式化距离和时间
            distance_str = f"{distance/1000:.1f}公里" if distance > 1000 else f"{distance}米"
            duration_min = duration // 60
            duration_str = f"{duration_min}分钟" if duration_min < 60 else f"{duration_min//60}小时{duration_min%60}分钟"
            
            mode_names = {
                "driving": "驾车",
                "walking": "步行",
                "transit": "公交",
                "riding": "骑行"
            }
            
            result = f"🗺️ {mode_names.get(mode, '驾车')}路线规划：\n\n"
            result += f"起点: {origin}\n"
            result += f"终点: {destination}\n"
            result += f"距离: {distance_str}\n"
            result += f"预计时间: {duration_str}\n\n"
            
            # 显示步骤
            steps = path.get("steps", [])
            if steps:
                result += "路线指引：\n"
                for i, step in enumerate(steps[:10], 1):  # 只显示前10步
                    instruction = step.get("instruction", "")
                    step_distance = step.get("distance", "")
                    result += f"{i}. {instruction} ({step_distance})\n"
                if len(steps) > 10:
                    result += f"... 还有 {len(steps) - 10} 个步骤\n"
            
            return result
        else:
            return f"❌ 路径规划失败: {data.get('info', '未知错误')}"
    except Exception as e:
        return f"❌ 请求失败: {str(e)}"


@tool
def get_weather(city: str) -> str:
    """
    天气查询 - 查询指定城市的天气

    Args:
        city: 城市名称或城市编码，例如 "北京" 或 "110000"
    """
    if not GAODE_API_KEY:
        return "❌ 请设置 GAODE_API_KEY 环境变量"
    
    try:
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {
            "key": GAODE_API_KEY,
            "city": city,
            "extensions": "all"
        }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{url}?{query}"
        
        req = urllib.request.Request(full_url, headers={"User-Agent": "LangGraph-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("status") == "1" and data.get("forecasts"):
            forecast = data["forecasts"][0]
            city_name = forecast.get("city", city)
            province = forecast.get("province", "")
            report_time = forecast.get("reporttime", "")
            
            result = f"🌤️ {province} {city_name} 天气预报\n"
            result += f"更新时间: {report_time}\n\n"
            
            # 未来几天预报
            casts = forecast.get("casts", [])
            for cast in casts[:3]:  # 显示3天
                date = cast.get("date", "")
                day_weather = cast.get("dayweather", "")
                night_weather = cast.get("nightweather", "")
                day_temp = cast.get("daytemp", "")
                night_temp = cast.get("nighttemp", "")
                day_wind = cast.get("daywind", "")
                day_power = cast.get("daypower", "")
                
                result += f"📅 {date}\n"
                result += f"  白天: {day_weather} {day_temp}°C\n"
                result += f"  夜间: {night_weather} {night_temp}°C\n"
                result += f"  风向: {day_wind}{day_power}\n\n"
            
            return result
        else:
            return f"❌ 天气查询失败: {data.get('info', '未知错误')}"
    except Exception as e:
        return f"❌ 请求失败: {str(e)}"


@tool
def get_district_info(keywords: str, subdistrict: int = 1) -> str:
    """
    行政区划查询 - 查询行政区划信息

    Args:
        keywords: 查询关键词，例如 "北京" 或 "110000"
        subdistrict: 显示下级行政区级数，默认1级
    """
    if not GAODE_API_KEY:
        return "❌ 请设置 GAODE_API_KEY 环境变量"
    
    try:
        url = "https://restapi.amap.com/v3/config/district"
        params = {
            "key": GAODE_API_KEY,
            "keywords": keywords,
            "subdistrict": subdistrict,
            "extensions": "all"
        }
        
        query = urllib.parse.urlencode(params)
        full_url = f"{url}?{query}"
        
        req = urllib.request.Request(full_url, headers={"User-Agent": "LangGraph-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get("status") == "1" and data.get("districts"):
            districts = data["districts"]
            if not districts:
                return f"❌ 未找到 '{keywords}' 的行政区划信息"
            
            district = districts[0]
            name = district.get("name", "")
            level = district.get("level", "")
            adcode = district.get("adcode", "")
            center = district.get("center", "")
            
            level_names = {
                "country": "国家",
                "province": "省份",
                "city": "城市",
                "district": "区县",
                "street": "街道"
            }
            
            result = f"🏛️ 行政区划信息：\n\n"
            result += f"名称: {name}\n"
            result += f"级别: {level_names.get(level, level)}\n"
            result += f"区划码: {adcode}\n"
            result += f"中心坐标: {center}\n"
            
            # 下级行政区
            sub_districts = district.get("districts", [])
            if sub_districts:
                result += f"\n包含 {len(sub_districts)} 个下级行政区：\n"
                for sub in sub_districts[:20]:  # 最多显示20个
                    sub_name = sub.get("name", "")
                    sub_level = sub.get("level", "")
                    result += f"  • {sub_name} ({level_names.get(sub_level, sub_level)})\n"
                if len(sub_districts) > 20:
                    result += f"  ... 还有 {len(sub_districts) - 20} 个\n"
            
            return result
        else:
            return f"❌ 行政区划查询失败: {data.get('info', '未知错误')}"
    except Exception as e:
        return f"❌ 请求失败: {str(e)}"
