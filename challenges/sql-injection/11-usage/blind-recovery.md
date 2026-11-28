---
summary: 检查 Daily Blogs 密码恢复功能是否会通过响应差异泄露数据库查询结果。
level: advanced
lab: usage
---

# 场景

Daily Blogs 为用户提供密码恢复功能。用户提交邮箱后，页面会返回处理结果，但不会直接显示数据库中的账户信息。

请从正常的密码恢复请求开始，比较不同输入条件下的响应，并判断应用是否泄露了可用于推断数据库内容的信息。

# 任务

利用密码恢复流程中的数据库查询缺陷，恢复后台管理员账户所需的信息，并取得 Web 应用运行账户的 User Flag。

```quiz
title: Blind Recovery
kind: flag
prompt: |
  通过密码恢复流程中的真实数据库响应差异，完成 Web foothold 并提交 User Flag。
answer: "TTP{usage_demo_user_only}"
match: trim
hint: 同时观察布尔条件与响应时间，不要假设页面必须直接回显查询结果。
```
