---
summary: 在 Markdown 文档分享网站上调查输入处理与管理员审阅行为，完成 Web 端权限边界测试。
level: medium
lab: alert
---

# 场景

Alert 提供在线 Markdown 预览和分享服务，网站团队会处理用户的联系消息。你需要从公开功能开始分析系统如何呈现和转发用户提交的数据。

# 任务

调查 Web 应用中的跨用户信任边界，设法读取指定的 Web 目标 Flag。本题不包括 Linux Root 提权。

```quiz
title: Web 安全目标
kind: flag
prompt: |
  从普通访问者身份出发，完成 Web 安全漏洞链并提交目标 Flag。
answer: "TTP{alert_default_web_flag}"
match: trim
hint: 关注 Markdown 分享后谁会打开它，以及哪些资源只能从应用服务器本机访问。
```
