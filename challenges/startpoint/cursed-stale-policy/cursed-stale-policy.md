---
summary: 调查 CSP 分析平台与自动化审阅流程，寻找策略状态和浏览器执行之间的信任边界。
level: advanced
lab: cursed-stale-policy
---

# 场景

一个在线 CSP 分析平台允许开发人员检查策略、提交测试内容，并查看浏览器报告。平台还提供自动化审阅功能，用于检查提交的内容在真实浏览器中的表现。

你已获得授权对该平台进行安全测试。请从公开页面和正常交互开始，理解策略分析、审阅任务和结果记录之间的关系。

# 任务

完成对 CSP 分析平台的安全测试，取得自动化审阅管理员持有的 Web Flag。

本题考察 CSP 策略、浏览器脚本执行、异步审阅流程和跨请求状态处理。不要求 Linux Root 提权。

~~~quiz
title: Recover the Reviewer's Flag
kind: flag
prompt: |
  从 CSP 分析平台的正常功能开始调查，理解策略与审阅流程之间的关系，最终取得管理员浏览器持有的 Web Flag。
answer: "TTP{cursed_stale_policy_default}"
match: trim
hint: 关注 CSP 响应头是否随请求变化，以及浏览器审阅任务实际使用的策略。
~~~
