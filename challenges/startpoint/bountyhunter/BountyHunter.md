---
summary: 从一个公开的漏洞悬赏门户开始，调查报告提交流程与后台票据验证工具。
level: easy
lab: bountyhunter
---

# 场景

一家名为 Bounty Hunters 的团队正在测试新的漏洞报告门户。首页可以正常浏览，但 Portal 页面仍标记为开发中，报告系统也只提供有限的测试功能。

你受委托检查这个 beta 系统。请从公开页面和正常报告提交流程开始，追踪 XML 数据如何被后台处理，并继续评估开发账户的系统权限。

# 任务

1. 调查漏洞报告系统的 XML 处理流程，取得 development 账户的访问权限并提交 User Flag。
2. 审计 development 账户被授予的 Skytrain 票据验证工具，取得 root 权限并提交 Root Flag。

~~~quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  从公开的报告门户开始调查，利用 XML 处理流程取得 development 账户权限，并提交 User Flag。
answer: "TTP{bountyhunter_user_default}"
match: trim
hint: 检查浏览器实际提交的数据格式，以及服务端解析 XML 时会访问哪些外部资源。
~~~

~~~quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: |
  从 development 账户继续检查系统授权与 Skytrain 票据验证流程，取得 root 权限并提交 Root Flag。
answer: "TTP{bountyhunter_root_default}"
match: trim
hint: 检查 sudo 允许执行的具体程序，以及该程序如何处理票据中的表达式。
~~~
