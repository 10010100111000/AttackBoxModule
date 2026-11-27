# Intense — Writeup

## 范围

本题复现 HTB Intense 的 Web 攻击路径：公开源码分析、访客登录、SQLite 条件错误注入提取管理员 secret、SHA-256 secret-prefix MAC 长度扩展伪造管理员会话，以及管理日志路径遍历读取 Web Flag。

本平台版本限定为 Web-only。原题后续 SNMP 命令执行、SSH 隧道和 native binary exploitation 不属于本题目标，不增加 Root Flag。

## 1. 侦察与正常业务

访问社区消息服务：

```bash
curl -i http://<TARGET>:8080/
```

首页提供登录入口和公开源码下载。下载并检查源码包：

```bash
curl -o src.zip http://<TARGET>:8080/src.zip
unzip -l src.zip
unzip -q src.zip -d source
```

先通过正常访客账户登录，再打开消息提交页面，使用普通短消息观察请求：

```bash
curl -i -c cookies.txt -b cookies.txt \
  -d 'username=guest&password=guest' http://<TARGET>:8080/postlogin
curl -i -b cookies.txt -d 'message=hello community' http://<TARGET>:8080/submitmessage
```

## 2. 分析消息写入与 SQLite 错误

检查 `app.py` 中的消息提交处理，以及 `utils.py` 中的过滤逻辑。输入被直接插入 SQL 字符串，且 SQLite 原生错误会返回到 HTTP 响应。

消息长度限制为 140 字符，并过滤少数指定词语。利用 SQLite `INSERT` 表达式上下文，可以将查询结果放入 `CASE` 条件中；当条件成立时调用超出 SQLite BLOB 大小限制的 `zeroblob()`，从而产生可区分的原生数据库错误。

## 3. 使用条件错误 Oracle 提取管理员 secret

通过逐字符比较查询 `users` 表中管理员的 `secret`。每次只测试一个十六进制字符，观察响应是否包含 `string or blob too big`。匹配时记录该字符，直到恢复完整的 64 位十六进制 SHA-256 值。

该值不是管理员明文密码；本题的下一步并不要求破解它，而是将它作为管理员会话中的 `secret` 字段使用。

## 4. 分析 LWT 会话签名

源码中的会话结构由分号分隔的键值对组成，签名计算方式为：

```python
sha256(SECRET + message)
```

这是不安全的 SHA-256 secret-prefix MAC。SHA-256 属于 Merkle–Damgard 结构，可对已知消息和签名执行长度扩展。服务启动时随机生成 8–15 字节密钥，因此对每种可能长度分别尝试。

原始访客会话中包含 `username=guest` 和访客 secret。将以下字段追加到已签名消息：

```text
;username=admin;secret=<recovered-admin-secret>;
```

解析器按顺序写入字典，后出现的同名键覆盖前面的访客值。只要猜中的密钥长度正确，扩展后的签名就能通过服务端校验。

## 5. 进入管理区域并利用日志路径遍历

携带伪造会话访问管理区域。管理页面提供日志查看功能，但文件路径直接与日志目录拼接，没有验证规范化后的路径是否仍处于日志目录内。

通过日志查看 POST 请求读取：

```text
../../home/analyst/user.txt
```

将返回的 TTP Flag 提交即可完成本题。

## 自动化验收

`exploit.py` 使用独立 HTTP 客户端按顺序执行源码发现、访客登录、SQLite 条件错误提取、SHA-256 长度扩展、管理员会话验证和最终文件读取。CI 会为每次运行生成随机 Flag，并与实际 HTTP 回读值逐字节比对。

攻击端只通过隔离 Docker 网络访问目标，不挂载目标文件系统、不使用 Docker socket，也不通过 `docker exec` 读取 Flag。

## 漏洞根因与修复

- SQL 注入：使用参数化查询，不要把用户输入拼接到 SQL 语句中。
- 错误信息泄露：生产环境不应将数据库内部错误原样返回给客户端。
- 会话签名：使用标准 HMAC-SHA-256，而不是 `SHA256(secret || message)`。
- 重复键解析：拒绝重复会话字段，或采用明确且不可歧义的结构化序列化格式。
- 路径遍历：规范化目标路径并确认其仍位于允许的日志根目录内。
