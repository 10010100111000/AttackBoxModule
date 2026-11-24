---
summary: 一处功能简单的博客网站对外开放。通过观察应用行为和可访问的功能，寻找从普通访问者到 Web 服务环境的利用路径。
level: medium
lab: nodeblog
---

# 场景

一家社区博客平台刚刚上线。网站提供公开文章浏览、账号登录，以及面向作者的内容编辑功能。你需要从外部访问者的视角调查服务，分析输入处理与信任边界，寻找能够影响服务端执行的漏洞。

# 任务

通过网站功能完成 Web 漏洞利用链，最终取得运行该 Web 应用的普通服务账户可读取的 Flag。此挑战不涉及 Linux Root 提权。

```quiz
title: Web 立足点
kind: flag
prompt: |
  完成博客应用的漏洞发现与利用，在获得 Web 服务执行能力后读取目标 Flag 并提交。
answer: "TTP{nodeblog_default_web_foothold_flag}"
match: trim
hint: 先观察身份认证对输入结构的处理，再检查登录后出现的内容管理功能。
```
