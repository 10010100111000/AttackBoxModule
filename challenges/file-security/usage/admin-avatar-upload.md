---
summary: 调查后台账户设置中的头像上传功能，评估文件类型校验、文件名与服务器端处理之间的信任边界。
level: intermediate
lab: usage
---

# 场景

Daily Blogs 的内容管理后台允许管理员修改个人资料，并上传头像。普通用户无法直接访问该后台。

在取得管理员访问能力后，检查头像上传功能如何验证文件，以及服务器如何保存和处理上传内容。

# 任务

利用真实后台上传组件中的文件处理缺陷，取得 Web 应用运行账户的执行权限，并提交 User Flag。

```quiz
title: Admin Avatar Upload
kind: flag
prompt: |
  调查管理员头像上传功能，利用真实文件处理缺陷取得 dash 的执行权限并提交 User Flag。
answer: "TTP{aaaaaaaaaaaaaaaa}"
match: trim
hint: 检查上传字段所使用的组件版本、实际保存路径，以及服务器对上传文件的处理方式。
```
