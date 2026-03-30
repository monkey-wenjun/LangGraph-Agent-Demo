# Web Search Skill - 网络搜索

## 描述
使用搜索引擎查询互联网上的最新信息，支持多种搜索类型。

## 适用场景
当用户需要以下信息时调用此技能：
- 查询最新的新闻资讯
- 搜索技术文档或教程
- 查找产品信息或评价
- 获取实时信息（天气、股价等）
- 验证某个事实或数据

## 工具函数

### web_search

执行网络搜索并返回相关结果。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| query | string | 是 | 搜索关键词 |
| num_results | number | 否 | 返回结果数量，默认 5，最大 10 |

**使用示例：**
```python
# 搜索最新新闻
web_search(query="2024年人工智能技术发展趋势")

# 搜索技术文档
web_search(query="Python FastAPI 教程", num_results=3)
```

### get_page_content

获取指定网页的完整内容。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| url | string | 是 | 网页 URL |

**使用示例：**
```python
# 获取网页内容
get_page_content(url="https://example.com/article")
```

## 注意事项
- 搜索结果可能包含广告，需要自行过滤
- 网页内容抓取可能受反爬虫机制限制
- 建议使用 `get_page_content` 获取详细内容时，先检查 URL 是否可访问

## 示例输出

```
🔍 搜索结果 (5条):

1. [Python FastAPI 官方文档](https://fastapi.tiangolo.com/)
   FastAPI 是一个现代、快速（高性能）的 Web 框架...

2. [FastAPI 入门教程 - 知乎](https://zhuanlan.zhihu.com/...)
   本文介绍如何使用 FastAPI 快速构建 API 服务...
```
