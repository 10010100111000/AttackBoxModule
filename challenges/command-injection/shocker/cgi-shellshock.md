---
summary: 调查 Web 服务调用系统脚本时如何处理请求环境信息。
level: advanced
lab: shocker
---

# 场景

一台 Web 服务器使用后台脚本执行常规系统维护任务。该脚本通过 Web 服务器的标准接口启动，接收请求相关的环境信息。

请评估脚本解释器对这些环境信息的处理是否安全。

# 任务

通过 Web 服务的正常请求路径验证后台脚本执行边界，取得脚本运行账户的权限，并提交目标 Flag。

~~~quiz
title: CGI Environment
kind: flag
prompt: |
  调查 Web 请求到后台脚本的执行过程，证明请求环境信息能够影响脚本解释器的行为，并取得对应 Flag。
answer: "TTP{shocker_user_default}"
match: trim
hint: 从正常 CGI 请求与脚本使用的解释器开始检查。
~~~
