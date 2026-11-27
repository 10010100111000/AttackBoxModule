---
summary: 已取得 shelly 用户的命令执行权限。审计该账户可用的系统管理程序及其权限边界。
level: easy
lab: shocker
---

# 场景

你已经获得服务器上一个普通账户的执行权限。系统管理员为该账户配置了有限的免密管理操作，以便执行日常维护。

请检查这些授权是否真正限制了高权限程序的能力。

# 任务

利用当前账户被授权执行的管理程序取得 root 权限，并提交 Root Flag。

~~~quiz
title: Perl Maintenance
kind: flag
prompt: |
  审计当前账户的 sudo 权限，利用实际授权的程序取得 root 权限并提交 Flag。
answer: "TTP{shocker_root_default}"
match: trim
hint: 不要只检查允许执行的命令名称，还要检查该程序本身能做什么。
~~~
