---
summary: 已取得 www-data 的命令执行权限。继续检查 sudo 配置、其他系统账户与定期执行的维护任务。
level: medium
lab: bashed
---

# 场景

你已经在一台 Web 服务器上取得低权限账户的命令执行能力。主机上存在一个由开发团队维护的脚本目录，系统也配置了定期执行的维护任务。

请检查这些脚本的所有权、可写权限与执行身份，判断是否存在权限边界错误。

# 任务

利用真实的本地权限配置取得 root 权限，并提交 Root Flag。

~~~quiz
title: Scheduled Maintenance
kind: flag
prompt: |
  调查当前账户能够影响的脚本与后台维护任务，取得 root 权限并提交 Flag。
answer: "TTP{bashed_root_default}"
match: trim
hint: 区分脚本的修改权限与脚本实际运行时的身份。
~~~
