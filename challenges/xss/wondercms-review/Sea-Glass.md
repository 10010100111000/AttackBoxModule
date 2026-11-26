---
summary: 调查独立出版网站的投稿审阅流程，找出管理员浏览器中的信任边界。
level: medium
lab: wondercms-xss
---

# 场景

Northbound Press 是一个独立出版网站，访客可以浏览文章，也可以向编辑团队提交网站供审核。编辑团队会使用自己的浏览器查看收到的投稿链接。

网站使用成熟的 CMS 管理内容。请从公开页面和正常投稿流程开始，了解网站如何处理提交的网址，以及编辑团队如何审阅这些内容。

# 任务

完成对网站的 Web 安全测试，取得编辑团队可访问的隐藏目标并提交 Flag。

本题专注于 Web 客户端与管理员会话的安全边界，不要求 Linux 提权。

```quiz
title: Sea Glass
kind: flag
prompt: |
  从公开网站开始调查投稿与编辑审阅流程，找到能够影响管理员浏览器的输入点，并取得隐藏的 Web 目标。
answer: "TTP{wondercms_demo_xss_only}"
match: trim
hint: 留意 CMS 登录页面如何使用 URL 参数，以及编辑团队打开投稿链接时实际访问的站点和路径。
```
