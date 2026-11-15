---
level: medium
summary: 某游戏门户网站上线了展示门户与内部管理控制台。你需要利用 SQL 注入突破外围认证并破解凭据，进一步通过模板注入漏洞达成代码执行并获取立足点。
---

# 任务目标

对游戏门户网站进行渗透测试，利用 SQL 注入漏洞获取内部管理凭据；登录内部管理后台，利用存储型服务端模板注入（SSTI）获取底层系统命令执行权限并获取 Flag。

```quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  分析前台登录接口中的 SQL 注入漏洞并转储管理用户哈希，解密凭据后访问内部管理后台（internal-administration.goodgames.htb）；在个人资料设置中注入 Jinja2 模板执行系统命令，读取 `/home/augustus/user.txt` 中的 Flag 并提交。
answer: "HTB{replace_this_with_your_goodgames_user_flag}"
match: trim
hint: 注入前台登录提取 MD5 哈希，在内部管理后台用户资料处构造 {{ ... }} 模板执行 payload。
```
