---
summary: 某科技公司正在开发新的技术门户。检查公开站点及其内容管理系统，了解应用暴露的信息，并取得 Web 服务的初始访问权限。
level: intermediate
lab: devvortex
---

# 场景

某科技公司正在开发新的技术门户。公开站点与内容管理系统由不同的虚拟主机提供服务，管理员使用 CMS 管理网站内容。

请从公开页面开始，检查目标的 HTTP 服务、站点结构和应用行为，逐步找出能够进入管理界面的线索。

# 任务

评估目标 Web 应用的安全性，并取得 Web 服务账户权限范围内的 Flag。

```quiz
title: 获取 Web Flag
kind: flag
prompt: |
  从公开技术门户开始进行枚举，利用应用中真实存在的安全缺陷获得 Web 服务执行上下文，并读取目标账户目录中的 Flag。
answer: "TTP{aaaaaaaaaaaaaaaa}"
match: trim
```
