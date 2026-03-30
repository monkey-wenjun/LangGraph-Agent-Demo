# Gaode Skill - 高德地图服务

## 描述
集成高德地图 API，提供地理编码、逆地理编码、POI 搜索、路径规划、天气查询、行政区划查询等功能。

## 适用场景
当用户需要以下服务时调用此技能：
- 查询地址对应的经纬度坐标
- 根据坐标查询地址信息
- 搜索附近的地点（如餐厅、酒店、景点）
- 规划驾车、步行、公交、骑行路线
- 查询城市天气
- 查询行政区划信息

## 工具函数

### geocode

将地址转换为经纬度坐标。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| address | string | 是 | 要解析的地址 |
| city | string | 否 | 指定城市 |

**使用示例：**
```python
# 解析北京天安门地址
geocode(address="北京市东城区天安门", city="北京")
```

### regeocode

将经纬度坐标转换为地址。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| longitude | float | 是 | 经度 |
| latitude | float | 是 | 纬度 |

**使用示例：**
```python
# 查询坐标对应的地址
regeocode(longitude=116.397428, latitude=39.90923)
```

### search_poi

搜索周边的地点（POI）。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keywords | string | 是 | 搜索关键词 |
| city | string | 否 | 城市名称 |
| types | string | 否 | POI 类型编码 |
| radius | int | 否 | 搜索半径（米），默认 3000 |
| offset | int | 否 | 返回结果数，默认 10 |

**使用示例：**
```python
# 搜索北京附近的麦当劳
search_poi(keywords="麦当劳", city="北京", offset=5)

# 搜索附近的加油站
search_poi(keywords="加油站", radius=5000)
```

### route_planning

规划从起点到终点的路线。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| origin | string | 是 | 起点坐标或地址 |
| destination | string | 是 | 终点坐标或地址 |
| mode | string | 否 | 出行方式：driving(驾车)、walking(步行)、transit(公交)、riding(骑行)，默认 driving |

**使用示例：**
```python
# 驾车路线规划
route_planning(origin="北京天安门", destination="北京首都国际机场", mode="driving")

# 步行路线（使用坐标）
route_planning(origin="116.397428,39.90923", destination="116.407526,39.90403", mode="walking")
```

### get_weather

查询指定城市的天气。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| city | string | 是 | 城市名称或城市编码 |

**使用示例：**
```python
# 查询北京天气
get_weather(city="北京")

# 使用城市编码查询
get_weather(city="110000")
```

### get_district_info

查询行政区划信息。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keywords | string | 是 | 查询关键词 |
| subdistrict | int | 否 | 下级行政区级数，默认 1 |

**使用示例：**
```python
# 查询北京市的行政区划
get_district_info(keywords="北京", subdistrict=2)

# 查询浙江省下属区县
get_district_info(keywords="浙江", subdistrict=1)
```

## 配置要求

需要在环境变量中设置高德 API Key：
```bash
export GAODE_API_KEY=your_gaode_api_key
```

获取方式：
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册账号并创建应用
3. 申请 Web 服务 API Key

## 返回示例

### geocode 返回
```
📍 地址解析结果：

地址: 北京市东城区天安门
坐标: 116.397428,39.90923
省份: 北京市
城市: 北京市
区县: 东城区
```

### search_poi 返回
```
🔍 搜索 '麦当劳' 找到 10 个结果：

1. 麦当劳(北京站店)
   📍 北京市东城区北京站街
   📞 010-12345678
   📏 距离: 500米

2. 麦当劳(王府井店)
   📍 北京市东城区王府井大街
   ...
```

### route_planning 返回
```
🗺️ 驾车路线规划：

起点: 北京天安门
终点: 北京首都国际机场
距离: 28.5公里
预计时间: 45分钟

路线指引：
1. 沿天安门东大街向东行驶 (500米)
2. 进入建国门内大街 (1.2公里)
3. ...
```

### get_weather 返回
```
🌤️ 北京市天气预报
更新时间: 2026-03-30 10:00:00

📅 2026-03-30
  白天: 晴 25°C
  夜间: 多云 15°C
  风向: 东南风3级

📅 2026-03-31
  ...
```

## 注意事项
- 需要申请高德地图 API Key
- 免费版有每日调用次数限制
- 坐标格式为 "经度,纬度"，例如 "116.397428,39.90923"
