---
summary: 从普通网站开始调查开发团队留下的工具与系统维护流程。
level: easy
lab: bashed
---

# 场景

一台服务器提供简单的网站，页面提到开发团队仍在维护内部工具。网站本身没有明显的管理入口，但主机可能暴露了未被公开链接的开发资源。

你受委托检查这台主机。请从公开网站与正常页面开始，调查 Web 服务能够访问的功能，以及这些功能背后的系统权限。

# 任务

1. 找到开发环境中暴露的交互工具，取得 Web 服务账户的执行权限并提交 User Flag。
2. 调查该账户可用的系统权限与后台维护任务，取得 root 权限并提交 Root Flag。

~~~quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  从公开网站开始侦察，发现开发团队留下的工具并取得 Web 服务账户的执行权限，提交 User Flag。
answer: "TTP{bashed_user_default}"
match: trim
hint: 检查未被首页直接链接的开发资源，以及它们提供的交互能力。
~~~

~~~quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: |
  从 Web 服务账户继续调查系统账户、脚本目录和后台任务，取得 root 权限并提交 Root Flag。
answer: "TTP{bashed_root_default}"
match: trim
hint: 留意由高权限账户定期执行的脚本，以及低权限账户能否修改这些脚本。
~~~
