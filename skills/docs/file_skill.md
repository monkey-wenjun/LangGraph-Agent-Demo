# File Skill - 文件操作

## 描述
安全地读取、写入、列出项目目录下的文件。所有操作都被限制在项目根目录内，防止目录遍历攻击。

## 适用场景
当用户需要以下操作时使用此技能：
- 查看项目中的文件内容
- 创建或修改项目文件
- 列出某个目录下的文件列表
- 浏览项目结构

## 工具函数

### read_file

读取指定路径的文本文件内容。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| path | string | 是 | 文件路径，可以是相对项目根目录的路径或绝对路径 |

**使用示例：**
```python
# 读取 README.md 文件
read_file(path="README.md")

# 读取配置文件
read_file(path="config/settings.yaml")
```

### write_file

将内容写入指定路径的文本文件（覆盖写入）。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| path | string | 是 | 文件路径 |
| content | string | 是 | 要写入的文本内容 |

**使用示例：**
```python
# 创建日志文件
write_file(
    path="logs/app.log",
    content="2024-01-01 Application started\n"
)
```

### list_dir

列出指定目录下的文件和子目录。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| path | string | 否 | 目录路径，默认为当前目录 "." |

**使用示例：**
```python
# 列出当前目录
list_dir()

# 列出指定目录
list_dir(path="src/components")
```

## 安全限制
- 所有路径都被限制在项目根目录（BASE_DIR）内
- 尝试访问项目根目录外的路径会返回 "路径越界" 错误
- 相对路径会自动解析为基于项目根目录的绝对路径

## 返回格式

### read_file 返回示例
```
【/project/README.md】内容:
```
# 项目标题

项目描述...
```
```

### list_dir 返回示例
```
📁 /project/src 内容:
  📂 components
  📂 utils
  📄 index.js
  📄 app.py
```
