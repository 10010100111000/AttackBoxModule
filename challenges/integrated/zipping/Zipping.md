---
summary: 调查一家手表商城与在线求职功能，分析外部文件和输入数据的处理流程。
level: medium
lab: zipping
---

# 场景

Zipping Watches 是一家线上手表商城，提供商品展示和在线简历提交。作为外部安全测试人员，你需要从正常页面和业务功能出发，寻找可以进一步接触服务端的漏洞链。

# 任务

通过 Web 应用中的漏洞获得普通 Web 服务权限，并读取目标 Flag。不涉及 Linux Root 提权。

```quiz
title: Web 目标
kind: flag
prompt: |
  调查商城及相关功能，利用发现的问题取得 Web 服务的执行能力并提交 Flag。
answer: "TTP{zipping_default_web_flag}"
match: trim
hint: 观察上传的压缩文件在服务器内如何处理，以及如何重新访问其中的文件。
```
