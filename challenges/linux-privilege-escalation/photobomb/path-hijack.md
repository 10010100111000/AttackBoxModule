---
summary: 已取得 wizard 用户权限。审计系统维护脚本调用外部命令时的环境与路径信任。
level: easy
lab: photobomb
---

# 场景

你已经获得照片打印服务运行账户的执行权限。系统管理员为该账户配置了一项免密维护操作，用于整理原始图片文件。

请检查维护脚本如何定位并调用系统程序，以及当前用户是否能够影响该过程。

# 任务

利用维护操作中的权限边界问题取得 root 权限，并提交 Root Flag。

~~~quiz
title: Maintenance Path
kind: flag
prompt: |
  审计当前账户可执行的免密维护脚本，取得 root 权限并提交 Root Flag。
answer: "TTP{photobomb_root_default}"
match: trim
hint: 检查脚本调用的命令是否使用绝对路径，以及 sudo 是否允许传递环境变量。
~~~
