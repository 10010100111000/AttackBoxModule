---
summary: 调查社区注册服务的异常响应与编辑部投稿审核流程。
level: medium
lab: django-debug-xss
---

# 场景

Harbor Registry 是一个社区资料登记网站。访客可以注册公开用户名，也可以向编辑部提交个人主页供审核。编辑部会使用自己的浏览器查看收到的链接。

请从正常注册和投稿功能开始，观察应用如何处理重复资料，以及异常响应是否泄露了超出预期的信息。

# 任务

完成对 Harbor Registry 的 Web 安全测试，取得编辑部权限下的隐藏目标并提交 Flag。

本题考察真实 Django 错误页面中的客户端脚本注入，以及管理员浏览器与普通访客之间的会话边界。不要求 Linux 提权。

```quiz
title: Harbor Lights
kind: flag
prompt: |
  从公开注册功能开始调查，分析重复资料触发的异常响应，并结合编辑部的链接审核流程取得受保护的 Web 目标。
answer: "TTP{q7m2v5k4n6p3xwaz}"
match: trim
hint: 留意应用在处理重复用户名时返回的详细错误页面，以及编辑部浏览器访问投稿链接时所处的会话环境。
```
