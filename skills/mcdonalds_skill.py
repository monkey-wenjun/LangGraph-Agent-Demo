"""
McDonald's Skill - 麦当劳服务
基于 FastMCP 实现的麦当劳 API 服务
"""

import os
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool, BaseTool
from .base import Skill


class McDonaldsSkill(Skill):
    """麦当劳服务 Skill"""

    @property
    def name(self) -> str:
        return "mcdonalds"

    @property
    def description(self) -> str:
        return "麦当劳餐厅查询、菜单浏览、订单服务"

    def get_tools(self) -> List[BaseTool]:
        return [
            find_nearby_restaurants,
            get_menu,
            get_meal_categories,
            calculate_nutrition,
            check_promotions
        ]


# 麦当劳 API 配置
MCD_API_BASE = "https://open.mcd.cn/api/v1"


def _make_request(endpoint: str, params: Dict[str, Any] = None) -> Dict:
    """发送请求到麦当劳 API"""
    url = f"{MCD_API_BASE}{endpoint}"
    if params:
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "LangGraph-Agent/1.0"
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e), "message": "API 请求失败"}


@tool
def find_nearby_restaurants(
    latitude: float,
    longitude: float,
    radius: int = 5000,
    limit: int = 10
) -> str:
    """
    查找附近的麦当劳餐厅

    Args:
        latitude: 纬度，例如 31.2304
        longitude: 经度，例如 121.4737
        radius: 搜索半径（米），默认 5000
        limit: 返回结果数量，默认 10
    """
    # 模拟 API 响应（实际项目中调用真实 API）
    restaurants = [
        {
            "id": "MCD001",
            "name": "麦当劳上海南京东路餐厅",
            "address": "上海市黄浦区南京东路 100 号",
            "distance": 1200,
            "business_hours": "06:00-23:00",
            "services": ["麦乐送", "得来速", "24小时"],
            "phone": "021-12345678"
        },
        {
            "id": "MCD002",
            "name": "麦当劳上海人民广场餐厅",
            "address": "上海市黄浦区西藏中路 268 号",
            "distance": 2300,
            "business_hours": "24小时",
            "services": ["麦乐送", "24小时", "麦咖啡"],
            "phone": "021-87654321"
        },
        {
            "id": "MCD003",
            "name": "麦当劳上海外滩餐厅",
            "address": "上海市黄浦区中山东一路 18 号",
            "distance": 3500,
            "business_hours": "07:00-22:00",
            "services": ["麦乐送", "麦咖啡"],
            "phone": "021-11223344"
        }
    ]
    
    result = f"🍟 找到 {len(restaurants)} 家附近麦当劳餐厅：\n\n"
    for i, r in enumerate(restaurants[:limit], 1):
        result += f"{i}. {r['name']}\n"
        result += f"   📍 地址: {r['address']}\n"
        result += f"   📏 距离: {r['distance']} 米\n"
        result += f"   ⏰ 营业时间: {r['business_hours']}\n"
        result += f"   🛎️ 服务: {', '.join(r['services'])}\n"
        result += f"   📞 电话: {r['phone']}\n\n"
    
    return result


@tool
def get_menu(category: Optional[str] = None) -> str:
    """
    获取麦当劳菜单

    Args:
        category: 菜单分类，可选值：burger(汉堡), chicken(鸡肉), fries(小食), 
                 drink(饮品), dessert(甜品), breakfast(早餐), happy_meal(开心乐园餐)
                 不传则返回所有分类
    """
    menu_data = {
        "burger": {
            "name": "🍔 汉堡",
            "items": [
                {"name": "巨无霸", "price": 25.5, "desc": "双层牛肉饼配特制酱料"},
                {"name": "麦辣鸡腿汉堡", "price": 22.0, "desc": "酥脆鸡腿肉配香辣酱"},
                {"name": "板烧鸡腿堡", "price": 24.0, "desc": "炭烤鸡腿肉配新鲜蔬菜"},
                {"name": "双层吉士汉堡", "price": 21.0, "desc": "双层牛肉配双层芝士"},
                {"name": "安格斯厚牛芝士堡", "price": 35.0, "desc": "100%安格斯牛肉"}
            ]
        },
        "chicken": {
            "name": "🍗 鸡肉",
            "items": [
                {"name": "麦辣鸡翅(2块)", "price": 11.0, "desc": "香辣酥脆"},
                {"name": "麦乐鸡(5块)", "price": 13.5, "desc": "经典鸡块配蘸酱"},
                {"name": "脆汁鸡", "price": 15.0, "desc": "多汁酥脆鸡腿"},
                {"name": "麦麦脆汁鸡套餐", "price": 29.0, "desc": "包含薯条和饮料"}
            ]
        },
        "fries": {
            "name": "🍟 小食",
            "items": [
                {"name": "薯条(中)", "price": 12.0, "desc": "金黄酥脆"},
                {"name": "薯条(大)", "price": 14.0, "desc": "更大份量"},
                {"name": "洋葱圈", "price": 13.5, "desc": "香酥洋葱圈"},
                {"name": "玉米杯", "price": 9.5, "desc": "香甜玉米粒"}
            ]
        },
        "drink": {
            "name": "🥤 饮品",
            "items": [
                {"name": "可乐(中)", "price": 10.0, "desc": "可口可乐"},
                {"name": "雪碧(中)", "price": 10.0, "desc": "清爽柠檬味"},
                {"name": "麦咖啡拿铁", "price": 16.0, "desc": "香浓咖啡"},
                {"name": "橙汁", "price": 12.0, "desc": "100%纯果汁"},
                {"name": "奶昔(草莓)", "price": 15.0, "desc": "香滑奶昔"}
            ]
        },
        "dessert": {
            "name": "🍦 甜品",
            "items": [
                {"name": "甜筒", "price": 5.0, "desc": "经典香草冰淇淋"},
                {"name": "麦旋风(Oreo)", "price": 13.5, "desc": "Oreo饼干碎冰淇淋"},
                {"name": "新地(草莓)", "price": 12.0, "desc": "草莓酱冰淇淋"},
                {"name": "苹果派", "price": 8.0, "desc": "热乎乎苹果派"}
            ]
        },
        "breakfast": {
            "name": "🌅 早餐",
            "items": [
                {"name": "猪柳蛋麦满分", "price": 18.0, "desc": "经典早餐汉堡"},
                {"name": "热香饼", "price": 16.0, "desc": "配枫糖浆和黄油"},
                {"name": "吉士蛋麦满分", "price": 14.0, "desc": "鸡蛋配芝士"},
                {"name": "脆薯饼", "price": 8.0, "desc": "香脆土豆饼"}
            ]
        },
        "happy_meal": {
            "name": "🎁 开心乐园餐",
            "items": [
                {"name": "汉堡开心乐园餐", "price": 22.0, "desc": "汉堡+小薯+小饮+玩具"},
                {"name": "麦乐鸡开心乐园餐", "price": 22.0, "desc": "4块麦乐鸡+小薯+小饮+玩具"},
                {"name": "鱼排堡开心乐园餐", "price": 24.0, "desc": "鱼排堡+小薯+小饮+玩具"}
            ]
        }
    }
    
    if category and category in menu_data:
        cat = menu_data[category]
        result = f"{cat['name']} 菜单：\n\n"
        for item in cat["items"]:
            result += f"• {item['name']} - ¥{item['price']}\n"
            result += f"  {item['desc']}\n\n"
        return result
    
    # 返回所有分类
    result = "🍟 麦当劳完整菜单：\n\n"
    for key, cat in menu_data.items():
        result += f"\n{cat['name']}：\n"
        for item in cat["items"][:3]:  # 只显示前3个
            result += f"  • {item['name']} ¥{item['price']}\n"
        result += f"  ... 共 {len(cat['items'])} 款商品\n"
    
    result += "\n💡 使用 get_menu(category='burger') 查看特定分类"
    return result


@tool
def get_meal_categories() -> str:
    """获取所有套餐分类"""
    categories = [
        {"id": "burger", "name": "汉堡", "icon": "🍔", "desc": "经典汉堡和特色汉堡"},
        {"id": "chicken", "name": "鸡肉", "icon": "🍗", "desc": "麦乐鸡、鸡翅等鸡肉产品"},
        {"id": "fries", "name": "小食", "icon": "🍟", "desc": "薯条、洋葱圈等小食"},
        {"id": "drink", "name": "饮品", "icon": "🥤", "desc": "软饮、咖啡、奶昔"},
        {"id": "dessert", "name": "甜品", "icon": "🍦", "desc": "冰淇淋、派等甜品"},
        {"id": "breakfast", "name": "早餐", "icon": "🌅", "desc": "早餐时段专属菜单"},
        {"id": "happy_meal", "name": "开心乐园餐", "icon": "🎁", "desc": "儿童套餐含玩具"}
    ]
    
    result = "🍟 麦当劳菜单分类：\n\n"
    for cat in categories:
        result += f"{cat['icon']} {cat['name']} (category='{cat['id']}')\n"
        result += f"   {cat['desc']}\n\n"
    
    return result


@tool
def calculate_nutrition(items: List[str]) -> str:
    """
    计算餐品的营养信息

    Args:
        items: 餐品名称列表，例如 ["巨无霸", "薯条(大)", "可乐(中)"]
    """
    # 营养数据库（每份）
    nutrition_db = {
        "巨无霸": {"calories": 550, "protein": 25, "fat": 30, "carbs": 45},
        "麦辣鸡腿汉堡": {"calories": 520, "protein": 22, "fat": 28, "carbs": 48},
        "板烧鸡腿堡": {"calories": 480, "protein": 24, "fat": 24, "carbs": 42},
        "双层吉士汉堡": {"calories": 450, "protein": 23, "fat": 26, "carbs": 35},
        "安格斯厚牛芝士堡": {"calories": 620, "protein": 32, "fat": 38, "carbs": 40},
        "麦辣鸡翅(2块)": {"calories": 190, "protein": 12, "fat": 14, "carbs": 6},
        "麦乐鸡(5块)": {"calories": 220, "protein": 13, "fat": 13, "carbs": 10},
        "薯条(中)": {"calories": 320, "protein": 4, "fat": 16, "carbs": 42},
        "薯条(大)": {"calories": 480, "protein": 6, "fat": 24, "carbs": 63},
        "可乐(中)": {"calories": 200, "protein": 0, "fat": 0, "carbs": 52},
        "麦旋风(Oreo)": {"calories": 280, "protein": 6, "fat": 12, "carbs": 38},
        "甜筒": {"calories": 150, "protein": 3, "fat": 6, "carbs": 22}
    }
    
    total = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
    found_items = []
    
    for item in items:
        item_clean = item.strip()
        if item_clean in nutrition_db:
            data = nutrition_db[item_clean]
            for key in total:
                total[key] += data[key]
            found_items.append(item_clean)
    
    if not found_items:
        return "❌ 未找到指定餐品的营养信息，请检查餐品名称是否正确。"
    
    result = f"🍟 {', '.join(found_items)} 的营养信息：\n\n"
    result += f"🔥 热量: {total['calories']} 千卡\n"
    result += f"🥩 蛋白质: {total['protein']} 克\n"
    result += f"🧈 脂肪: {total['fat']} 克\n"
    result += f"🍞 碳水化合物: {total['carbs']} 克\n\n"
    
    # 健康建议
    if total['calories'] > 800:
        result += "⚠️ 热量较高，建议搭配运动或分餐食用"
    elif total['calories'] < 400:
        result += "✅ 热量适中，可以作为轻食"
    else:
        result += "✅ 营养均衡的正餐选择"
    
    return result


@tool
def check_promotions() -> str:
    """查询当前促销活动"""
    promotions = [
        {
            "title": "🎉 周一至周五早餐套餐半价",
            "desc": "上午5:00-10:30，早餐套餐享5折优惠",
            "valid_until": "2026-04-30"
        },
        {
            "title": "🍟 薯条买一送一",
            "desc": "购买大份薯条，赠送中份薯条",
            "valid_until": "2026-03-31"
        },
        {
            "title": "📱 App首单立减10元",
            "desc": "麦当劳App新用户首单立减10元",
            "valid_until": "长期有效"
        },
        {
            "title": "🎁 开心乐园餐玩具上新",
            "desc": "最新迪士尼系列玩具",
            "valid_until": "2026-04-15"
        },
        {
            "title": "☕ 麦咖啡买二送一",
            "desc": "购买两杯麦咖啡，赠送一杯",
            "valid_until": "2026-03-25"
        }
    ]
    
    result = "🎁 当前促销活动：\n\n"
    for i, promo in enumerate(promotions, 1):
        result += f"{i}. {promo['title']}\n"
        result += f"   {promo['desc']}\n"
        result += f"   有效期至: {promo['valid_until']}\n\n"
    
    result += "💡 下载麦当劳App获取更多优惠！"
    return result
