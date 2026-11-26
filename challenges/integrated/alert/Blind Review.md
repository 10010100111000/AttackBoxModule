---
summary: 调查 Markdown 分享与管理员审阅流程，利用 Web 信任边界取得隐藏目标。
level: medium
lab: alert
---

# 场景

一个在线 Markdown 服务允许访客上传文档、生成分享链接，并通过联系表单请求站点团队审阅内容。站点团队会使用自己的浏览器处理收到的分享链接。

你需要从普通访客能够接触到的功能入手，弄清楚文档在上传、分享和审阅过程中如何被处理，以及不同访问位置之间存在什么差异。

# 任务

完成对 Alert Web 应用的安全测试，取得隐藏的 Web 目标并提交 Flag。

本题考察 Web 应用中的内容处理、跨用户信任边界和服务器本地资源访问。不要求 Linux Root 提权，也不需要 AttackBox 之外的额外工具环境。

```quiz
title: Blind Review
kind: flag
prompt: |
  从公开的 Markdown 服务开始调查，沿着文档分享和站点审阅流程寻找可利用的信任边界，最终取得 Web 目标并提交 Flag。
answer: "TTP{alert_default_web_flag}"
match: trim
hint: 关注上传内容如何被渲染、分享链接由谁打开，以及服务器本地资源与普通访客可访问资源之间的区别。
```
