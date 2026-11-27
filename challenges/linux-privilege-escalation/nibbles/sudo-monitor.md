---
summary: 已取得 nibbler 用户的命令执行权限。检查本地文件、监控任务与受限管理操作，判断是否存在权限边界错误。
level: easy
lab: nibbles
---

# 场景

你已经在这台博客服务器上取得了普通服务账户的命令执行权限。系统管理员配置了一项用于维护主机状态的监控任务，并限制该账户只能通过指定入口执行管理操作。

请审计当前账户能够修改的文件，以及这些文件在不同权限上下文中的执行方式。

# 任务

在当前 nibbler 用户上下文中调查本地权限配置，取得 root 权限并提交 Root Flag。

~~~quiz
title: System Monitor
kind: flag
prompt: |
  检查当前账户可访问的本地文件和管理权限，利用真实存在的权限配置错误取得 root 权限并提交 Flag。
answer: "TTP{nibbles_root_default}"
match: trim
hint: 关注被授权执行的脚本本身由谁拥有，以及当前账户是否能够修改它。
~~~
