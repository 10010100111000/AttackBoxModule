---
summary: 一家日常博客平台提供账户注册、密码恢复与内容管理后台。评估从公开账户流程到服务器权限边界的完整安全链。
level: hard
lab: usage
---

# 场景

Daily Blogs 是一个提供日常文章与用户账户服务的网站。访客可以注册账户、恢复密码并浏览公开内容。站点还为内容管理员提供独立的后台入口。

请从公开业务功能开始，分析账户恢复、后台内容管理和服务器运维之间的关系。

# 任务

1. 从公开账户流程开始，取得 Web 应用运行账户的执行权限，并提交 User Flag。
2. 继续调查系统账户与维护程序，取得 root 权限并提交 Root Flag。

```quiz
title: Web foothold (User Flag)
kind: flag
prompt: |
  从 Daily Blogs 的账户功能开始调查，取得应用运行账户 dash 的权限并读取 /home/dash/user.txt。
answer: "TTP{usage_demo_user_only}"
match: trim
hint: 先区分正常注册与密码恢复请求，比较不同输入条件下服务器响应的差异。
```

```quiz
title: System privilege (Root Flag)
kind: flag
prompt: |
  从 dash 的权限继续调查，取得 xander 账户并利用其维护权限读取 /root/root.txt。
answer: "TTP{usage_demo_root_only}"
match: trim
hint: 不要只检查 sudo 命令本身。注意它调用的归档工具如何解释传入的文件列表。
```
