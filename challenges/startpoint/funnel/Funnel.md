---
level: easy
summary: 某运维团队配置了文件传输与远程接入服务，但内部核心数据库仅监听在本地环回地址。你需要通过信息收集获得接入通道，并构建本地流量隧道获取核心数据。
---

# 任务目标

利用匿名 FTP 服务检索敏感运维备份信息并恢复认证凭据，登录 SSH 建立端口转发隧道突破本地访问限制，最终从内部数据库中提取目标 Flag。

```quiz
title: 获取数据库 Flag
kind: flag
prompt: |
  连接匿名 FTP 服务获取备份邮件与密码策略，推导出 SSH 登录凭据；通过 SSH 本地端口转发建立连接至内部仅监听 127.0.0.1 的 PostgreSQL 数据库（secrets 库），查询 flag 表并提交其中的 Flag。
answer: "FLAG{replace_this_with_your_own_funnel_database_flag}"
match: trim
hint: 使用 ssh -L 本地端口:127.0.0.1:5432 建立本地隧道后通过 psql 查询。
```
