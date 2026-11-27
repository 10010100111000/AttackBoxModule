---
summary: 从网络管理平台的正常页面开始，调查旧版管理程序、内部应用与系统权限之间的信任边界。
level: medium
lab: openadmin
---

# 场景

一台主机运行着网络管理平台，供管理员维护内部网络资产。平台同时连接数据库，并与一套仅供内部访问的管理应用共享部分账户信息。

你受委托评估这台主机。请从公开管理页面开始，逐步调查应用接口、内部服务和系统管理权限。

# 任务

1. 识别管理平台的版本与可访问功能，取得普通系统账户的访问权限并提交 User Flag。
2. 继续检查内部应用与 SSH 身份认证，取得 Joanna 用户权限。
3. 审计 Joanna 可执行的管理操作，取得 root 权限并提交 Root Flag。

~~~quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  从公开的 OpenNetAdmin 管理页面开始调查，追踪数据库凭据、内部应用和 SSH 密钥之间的关系，取得 Joanna 用户权限并提交 User Flag。
answer: "TTP{openadmin_user_default}"
match: trim
hint: 先识别 OpenNetAdmin 版本，再检查其 AJAX 功能和内部服务访问边界。
~~~

~~~quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: |
  从 Joanna 用户继续检查 sudo 授权的管理工具，取得 root 权限并提交 Root Flag。
answer: "TTP{openadmin_root_default}"
match: trim
hint: 关注被授权程序自身提供的交互功能，而不仅是它打开的文件。
~~~
