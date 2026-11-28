---
summary: 检查 Daily Blogs 密码恢复功能是否会通过响应差异泄露数据库查询结果。
level: advanced
lab: usage
---

# 场景

Daily Blogs 为用户提供密码恢复功能。用户提交邮箱后，页面会返回处理结果，但不会直接显示数据库中的账户信息。

请从正常的密码恢复请求开始，比较不同输入条件下的响应，并判断应用是否泄露了可用于推断数据库内容的信息。

# 任务

利用密码恢复流程中的数据库查询缺陷，通过布尔/时间盲注提取管理员记录中的持久登录令牌，并提交数据库 Flag。

```quiz
title: Blind Recovery
kind: flag
prompt: |
  通过密码恢复流程中的真实数据库响应差异，提取 admin_users.remember_token 并提交数据库 Flag。
answer: "TTP{usage_database_seed_default}"
match: trim
hint: 同时观察布尔条件与响应时间，不要假设页面必须直接回显查询结果。
```
