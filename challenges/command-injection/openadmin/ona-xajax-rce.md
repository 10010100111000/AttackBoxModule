---
summary: 调查 OpenNetAdmin 的 AJAX 功能，确认旧版本如何处理网络诊断参数。
level: medium
lab: openadmin
---

# 场景

你已经发现一套用于管理网络资产的 OpenNetAdmin 平台。平台提供网络诊断功能，允许管理员检查设备的连通性。

请检查该功能如何处理请求参数，以及这些参数是否会影响服务器端命令的执行。

# 任务

通过真实的管理平台接口取得 Web 服务账户的命令执行权限，继续完成凭据调查并取得 User Flag。

~~~quiz
title: Network Diagnostics
kind: flag
prompt: |
  调查 OpenNetAdmin 的 AJAX 网络诊断功能，验证参数处理是否会影响服务器端命令，并沿凭据复用路径取得 User Flag。
answer: "TTP{openadmin_user_default}"
match: trim
hint: 从版本信息与 xajax 请求流程开始检查，留意诊断功能调用的系统工具。
~~~
