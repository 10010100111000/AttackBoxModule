---
summary: 从一个简单的博客首页开始，发现隐藏的 CMS 管理入口，调查插件上传功能与主机上的监控脚本权限。
level: easy
lab: nibbles
---

# 场景

一台小型博客服务器只展示着一条简单的欢迎信息。站点看起来并没有复杂功能，但服务器仍保留着 CMS 管理后台与旧版插件。

你受委托检查这台主机。请从公开页面和正常的 CMS 功能开始，逐步发现文件上传与本地权限配置中的问题。

# 任务

1. 识别站点使用的 CMS 与版本，进入管理后台并调查插件功能。
2. 利用真实存在的插件文件处理缺陷取得主机初始访问权限。
3. 检查用户目录中的文件与 sudo 权限，完成本地提权。

~~~quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  从公开站点开始侦察，发现并利用 CMS 插件上传问题，取得 nibbler 用户权限并提交 User Flag。
answer: "TTP{nibbles_user_default}"
match: trim
hint: 查看首页源码中的路径线索，再识别 CMS 版本与原生插件功能。
~~~

~~~quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: |
  从 nibbler 用户继续检查本地文件、归档内容与 sudo 权限，取得 root 权限并提交 Root Flag。
answer: "TTP{nibbles_root_default}"
match: trim
hint: 注意 sudo 允许执行的脚本是否也能被当前用户修改。
~~~
