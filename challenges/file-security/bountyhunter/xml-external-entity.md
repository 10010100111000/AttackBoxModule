---
summary: 调查报告门户如何解析客户端提交的 XML，以及解析器对外部实体的处理边界。
level: easy
lab: bountyhunter
---

# 场景

漏洞报告门户要求浏览器将报告字段编码为 XML，再提交给后台 tracker。系统仍处于 beta 阶段，尚未接入正式数据库。

请检查正常报告提交过程，并判断 XML 解析器是否会访问报告内容引用的外部资源。

# 任务

通过真实的 XML 解析行为读取应用配置中的测试凭据，并使用该凭据取得 development 账户的访问权限，提交 User Flag。

~~~quiz
title: XML External Entity
kind: flag
prompt: |
  从正常报告提交开始，检查 XML 外部实体处理行为，读取配置并取得 development 账户权限，提交 Flag。
answer: "TTP{bountyhunter_user_default}"
match: trim
hint: 观察 tracker 接收的 base64 XML，并考虑 PHP stream wrapper 对文件读取的影响。
~~~
