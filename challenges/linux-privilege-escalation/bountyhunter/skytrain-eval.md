---
summary: 已取得 development 账户权限。审计 Skytrain 票据验证工具的 sudo 授权与输入处理。
level: medium
lab: bountyhunter
---

# 场景

Skytrain Inc 使用一个 Python 脚本验证 Markdown 格式的内部票据。development 账户被允许通过 sudo 运行这个指定脚本，以便协助 QA 检查票据。

请检查验证器对票据编号和表达式的处理方式，以及这些输入在高权限上下文中的执行结果。

# 任务

利用票据验证器的真实输入处理缺陷取得 root 权限，并提交 Root Flag。

~~~quiz
title: Skytrain Ticket Validation
kind: flag
prompt: |
  审计 sudo 授权的 Python 票据验证器，利用其真实表达式求值行为取得 root 权限并提交 Flag。
answer: "TTP{bountyhunter_root_default}"
match: trim
hint: 不要只检查票据编号的格式；继续追踪验证器如何计算票据总额。
~~~
