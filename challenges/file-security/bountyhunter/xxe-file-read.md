---
summary: 调查漏洞报告系统对 XML 文档的解析行为，以及报告内容能否影响服务器端的数据读取。
level: medium
lab: bountyhunter
---

# 场景

漏洞报告系统接受研究人员提交的结构化报告，并在页面上返回解析结果。请评估服务器如何处理报告中的外部数据引用。

# 任务

通过报告提交功能读取服务器上的指定配置内容，恢复开发环境访问凭据，并提交 User Flag。

~~~quiz
title: Report Parser
kind: flag
prompt: |
  检查报告解析流程对外部实体的处理，利用真实文件读取行为取得 development 账户访问能力并提交 Flag。
answer: "TTP{bountyhunter_user_default}"
match: trim
hint: 先观察正常 XML 报告的提交与回显，再研究解析器对外部引用的处理。
~~~
