---
summary: 已取得 development 账户的 SSH 访问权限。检查该账户被授权执行的 Skytrain 工具及其输入文件处理方式。
level: medium
lab: bountyhunter
---

# 场景

开发团队部署了一个用于验证 Skytrain 车票的辅助程序。为了方便日常检查，development 账户可以通过 sudo 执行该程序。

请审计程序读取的文件格式、验证规则与执行权限之间的关系。

# 任务

利用真实的程序行为取得 root 权限，并提交 Root Flag。

~~~quiz
title: Skytrain Validator
kind: flag
prompt: |
  检查车票验证程序如何处理输入文件，利用实际存在的权限边界问题取得 root 权限并提交 Flag。
answer: "TTP{bountyhunter_root_default}"
match: trim
hint: 关注程序对票据内容的解释方式，以及它在 sudo 上下文中的执行身份。
~~~
