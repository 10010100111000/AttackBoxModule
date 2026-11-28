---
summary: 从公开的照片打印服务开始，评估图像处理流程与主机维护权限之间的边界。
level: medium
lab: photobomb
---

# 场景

一家公司提供在线照片打印服务。用户可以选择图片、调整尺寸，并下载转换后的文件。系统还运行着用于维护图片目录的后台任务。

请从公开网站和正常业务功能开始调查，评估应用处理用户输入时是否正确限制了外部程序的行为。

# 任务

1. 调查照片处理服务，取得应用运行账户的执行权限并提交 User Flag。
2. 继续审计该账户可用的系统维护权限，取得 root 权限并提交 Root Flag。

~~~quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  从照片打印服务的正常功能开始调查，取得应用运行账户的权限并提交 User Flag。
answer: "TTP{photobomb_user_default}"
match: trim
hint: 先理解正常图片转换请求，再检查应用如何处理用户选择的输出格式。
~~~

~~~quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: |
  从应用运行账户继续审计系统维护任务，取得 root 权限并提交 Root Flag。
answer: "TTP{photobomb_root_default}"
match: trim
hint: 检查维护脚本调用的外部程序，以及执行时使用的环境变量。
~~~
