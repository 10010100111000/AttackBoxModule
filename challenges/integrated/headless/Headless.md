---
summary: 从一个处于建设中的网站开始，调查支持请求、系统报告与主机权限边界。
level: beginner
lab: htb-headless
---

# Headless

## 场景

Headless 网站目前仍显示建设中页面，但支持团队已经开放了联系表单。网站还提供一项仅供内部人员使用的系统状态报告功能。

你获得了对该主机的授权测试权限。请像真实渗透测试一样，从公开页面和服务枚举开始，逐步理解请求处理、用户会话以及服务器端功能之间的关系。

## 任务

先取得 Web 服务运行账户的 User Flag，再继续调查主机上的本地权限配置，最终取得 Root Flag。

```quiz
title: User Flag
kind: flag
prompt: 获取 Headless Web 服务运行账户的 User Flag。
answer: "TTP{headless_user_flag}"
match: trim
hint: 不要只观察表单字段。记录完整请求与响应，注意服务器在拒绝某些输入时返回了哪些额外信息。
```

```quiz
title: Root Flag
kind: flag
prompt: 在取得 User Flag 后，继续完成本地权限边界调查并获取 Root Flag。
answer: "TTP{headless_root_flag}"
match: trim
hint: 检查当前账户允许执行的特权命令，阅读对应脚本的每一条命令，并特别留意它如何定位要执行的文件。
```
