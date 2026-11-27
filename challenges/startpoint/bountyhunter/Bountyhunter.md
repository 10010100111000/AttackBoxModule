---
summary: 从公开的漏洞悬赏网站开始，调查报告提交功能、内部文件读取与开发环境的权限边界。
level: medium
lab: bountyhunter
---

# 场景

一个漏洞悬赏平台开放了研究人员门户和报告提交功能。门户仍处于测试阶段，但网站已经接入了用于处理报告的后台程序。

你受委托评估这套系统。请从公开页面与正常报告流程开始，检查数据处理方式及其背后的内部服务。

# 任务

1. 调查报告处理流程，取得开发账户的初始访问权限并提交 User Flag。
2. 审计开发账户被授权执行的内部工具，取得 root 权限并提交 Root Flag。

~~~quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  从公开门户和报告提交功能开始调查，取得 development 账户的访问权限并提交 User Flag。
answer: "TTP{bountyhunter_user_default}"
match: trim
hint: 关注报告数据在客户端与服务器端之间如何传递和解析。
~~~

~~~quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: |
  从 development 账户继续调查内部工具与权限配置，取得 root 权限并提交 Root Flag。
answer: "TTP{bountyhunter_root_default}"
match: trim
hint: 检查被 sudo 授权的程序如何处理外部提供的文件内容。
~~~
