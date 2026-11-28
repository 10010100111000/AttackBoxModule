---
summary: 从一台普通 Web 服务器的公开页面开始，调查后台脚本与系统服务之间的执行边界。
level: medium
lab: shocker
---

# 场景

一台服务器提供简单的网站，同时运行着用于维护状态的后台脚本。网站没有明显的管理入口，但服务器仍需要处理来自客户端的请求。

你受委托评估这台主机的安全性。请从公开服务和正常请求开始，识别应用执行环境，并调查它与系统权限之间的关系。

# 任务

完成对该主机的安全评估：

1. 找到 Web 服务与后台脚本之间的信任边界，取得普通系统用户的执行权限并提交 User Flag。
2. 检查该用户可执行的管理操作，取得 root 权限并提交 Root Flag。

~~~quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  从公开网站和正常请求开始调查，取得后台脚本运行账户的执行权限，并提交 User Flag。
answer: "TTP{g3fqu7mopyf6k3fl}"
match: trim
hint: 留意 Web 服务将哪些请求信息传递给后台脚本解释器。
~~~

~~~quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: |
  从普通系统账户继续审计本机管理权限，取得 root 权限并提交 Root Flag。
answer: "TTP{52pixevt4yc2rhwz}"
match: trim
hint: 检查当前账户被允许以更高权限执行的程序，以及这些程序的实际用途。
~~~
