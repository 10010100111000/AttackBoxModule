---
summary: 一个资格赛注册站点会在注册时安全保存国家字段，却在账户页面再次使用该字段构造 SQL 查询。调查数据从写入到读取的完整生命周期。
level: intermediate
lab: validation
---

# 场景

一个线上资格赛正在开放注册。访客只需填写用户名并选择国家，注册后即可查看同一国家的其他参赛者。

页面看起来只是普通的注册表单。请从正常注册流程开始，观察应用如何保存用户提交的数据，以及账户页面如何读取这些数据。

# 任务

1. 调查注册与账户页面之间的数据流，利用真实的二阶 SQL 注入取得 Web 应用执行权限，读取 User Flag。
2. 继续检查应用配置与系统身份验证之间的关系，取得 root 权限并读取 Root Flag。

```quiz
title: Web foothold (User Flag)
kind: flag
prompt: |
  从资格赛注册流程开始调查，利用二阶 SQL 注入取得 Web 应用执行权限，并读取 /home/htb/user.txt。
answer: "TTP{validation_user_default}"
match: trim
hint: 注册请求本身并不是直接注入点。重点观察账户页面如何再次使用已保存的国家字段。
```

```quiz
title: Native authentication (Root Flag)
kind: flag
prompt: |
  从 Web foothold 继续调查应用配置与系统账户之间的关系，取得 root 权限并读取 /root/root.txt。
answer: "TTP{validation_root_default}"
match: trim
hint: 数据库文件读取能力不只可以查看普通系统文件，也可以检查 PHP 运行时配置。注意配置中的凭据是否在其他身份验证边界被重复使用。
```
