---
summary: 调查开发目录中暴露的交互式工具，理解 Web 请求如何转化为系统命令。
level: easy
lab: bashed
---

# 场景

一台 Web 服务器保留了供开发团队使用的内部工具。该工具通过浏览器提供交互界面，允许开发人员执行日常维护操作。

请从公开站点开始调查，判断该工具是否应该对普通 Web 访问者开放。

# 任务

通过网站实际提供的功能取得 Web 服务账户的命令执行权限，并提交 User Flag。

~~~quiz
title: Developer Console
kind: flag
prompt: |
  发现并调查开发工具的实际执行能力，取得 Web 服务账户的命令执行权限并提交 Flag。
answer: "TTP{bashed_user_default}"
match: trim
hint: 不要只检查首页链接；留意 Web 服务器上未公开链接的开发资源。
~~~
