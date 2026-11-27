---
summary: 已取得 Joanna 用户权限。检查 sudo 授权的编辑器及其交互式命令功能。
level: easy
lab: openadmin
---

# 场景

你已经获得主机上的 Joanna 用户权限。系统管理员为该账户配置了一项免密管理操作，允许其使用指定编辑器维护一个受保护的文件。

请审计该授权是否真正限制了编辑器的功能范围。

# 任务

利用被授权程序本身的功能取得 root 权限，并提交 Root Flag。

~~~quiz
title: Restricted Editor
kind: flag
prompt: |
  检查 sudo 授权的 nano 编辑器是否提供超出文件编辑范围的功能，取得 root 权限并提交 Flag。
answer: "TTP{openadmin_root_default}"
match: trim
hint: 了解 nano 的交互式快捷键和命令执行能力。
~~~
