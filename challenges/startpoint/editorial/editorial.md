---
summary: 从出版社的封面预览功能开始调查，追踪内部 API、开发账户与部署流程中的信任边界，最终取得 User 和 Root Flag。
level: medium
lab: editorial
---

# 场景

Editorial Tiempo Arriba 是一家面向新作者的独立出版社。网站开放了投稿和封面预览功能，内部还运行着供编辑团队使用的 API 与部署服务。

你受委托对这套环境进行安全评估。请从公开网站的正常功能开始，逐步调查服务器端请求、内部服务和部署账户之间的关系。

# 任务

完成对 Editorial 的 Web 与主机安全评估：

1. 找到服务器端请求功能能够访问的内部资源，取得开发账户的初始访问权限。
2. 检查开发账户可访问的项目历史与部署配置，进一步取得生产账户权限。
3. 审计生产账户的受限管理操作，完成本地提权并取得 Root Flag。

~~~quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  从公开的封面预览功能入手，调查内部 API 与开发账户，取得主机上的普通用户权限并提交 User Flag。
answer: "TTP{editorial_user_default}"
match: trim
hint: 留意封面预览请求由哪一端发起，以及内部服务是否只对本机开放。
~~~

~~~quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: |
  从开发账户继续调查项目历史与生产部署流程，利用实际存在的权限配置问题取得 root 权限并提交 Root Flag。
answer: "TTP{editorial_root_default}"
match: trim
hint: 当前部署文件不一定保留所有历史信息；同时检查生产账户允许执行的管理操作。
~~~
