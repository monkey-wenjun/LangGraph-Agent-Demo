# CLI Skill - 命令行工具

## 描述
执行安全的本地命令行工具，目前支持 dig 命令查询域名 DNS 解析记录。

## 适用场景
当用户需要以下信息时调用此技能：
- 查询域名的 IP 地址（A 记录）
- 查询域名的 IPv6 地址（AAAA 记录）
- 查询域名的邮件服务器（MX 记录）
- 查询域名的名称服务器（NS 记录）
- 查询域名的文本记录（TXT 记录）
- 查询域名的别名记录（CNAME 记录）

## 工具函数

### dig_query

查询域名的 DNS 解析记录。

**参数：**
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| domain | string | 是 | 要查询的域名，例如 "example.com" |
| record_type | string | 否 | DNS 记录类型，默认为 "A"，可选值：A, AAAA, MX, NS, TXT, CNAME |

**使用示例：**

```python
# 查询 example.com 的 A 记录
dig_query(domain="example.com", record_type="A")

# 查询 baidu.com 的 MX 记录
dig_query(domain="baidu.com", record_type="MX")

# 查询 google.com 的 NS 记录
dig_query(domain="google.com", record_type="NS")
```

**返回值：**
- 成功：返回查询结果，包含解析到的 IP 地址或记录值
- 失败：返回错误信息

## 安全说明
- 所有用户输入都经过字符白名单过滤，只允许字母、数字、点、横线、下划线
- 命令执行有 15 秒超时限制
- 使用 `+short` 参数只返回关键信息

## 依赖
系统需要安装 `dig` 命令：
```bash
# Ubuntu/Debian
sudo apt-get install dnsutils

# CentOS/RHEL
sudo yum install bind-utils
```
