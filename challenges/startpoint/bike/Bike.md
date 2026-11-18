---
summary: 某自行车租赁系统上线了新版邮件订阅与展示服务。你需要对其 Web 服务展开安全评估，发现并利用模板引擎缺陷获取系统初始控制权与 Flag。
level: easy
lab: bike
---

# 场景

某自行车租赁系统上线了新版邮件订阅与展示服务。你需要对其 Web 服务展开安全评估，发现并利用模板引擎缺陷获取系统初始控制权与 Flag。

# 任务

对目标 Web 应用进行黑盒渗透测试，寻找并利用服务端模板注入（SSTI）漏洞，执行系统命令读取系统内部的 Flag。

```quiz
title: 获取 Root Flag
kind: flag
prompt: |
  对目标 Web 站点（端口 80）展开探测，发现并利用服务端模板引擎注入（SSTI）安全缺陷，执行任意系统命令并读取 `/root/flag.txt` 中的 Flag 并提交。
answer: "HTB{local_bike_training_flag_not_the_official_flag}"
match: trim
hint: 目标使用了 Handlebars 模板引擎，尝试通过原型链遍历并调用 child_process 执行系统命令。
```
