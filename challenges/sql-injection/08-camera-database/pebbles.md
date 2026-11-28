---
summary: 一台视频监控服务器公开了多个 Web 服务。通过服务枚举与目录发现，定位真实 ZoneMinder 控制台，并评估其日志查询功能与数据库权限边界。
level: advanced
lab: pebbles
---

# 场景

一台视频监控服务器对外提供多个服务。不同 HTTP 端口展示着不同页面，其中一个服务使用了历史版本的视频监控管理系统。

请从端口枚举和正常页面浏览开始，识别真正的应用入口，调查其日志查询请求与数据库之间的关系。

# 任务

完成对该主机的安全评估。利用真实应用漏洞取得容器内 root 权限，并读取目标文件中的 Flag。

~~~quiz
title: Camera Database
kind: flag
prompt: |
  从公开服务和正常页面开始调查，发现并利用 ZoneMinder 的真实 SQL 注入及后续数据库权限链，读取 /root/proof.txt 并提交其中的 Flag。
answer: "TTP{pebbles_unverified_demo_not_for_release}"
match: trim
hint: 不要只关注默认首页。先确认非标准 HTTP 端口实际运行的服务，再检查 ZoneMinder 日志查询请求中的参数如何进入 SQL。
~~~
