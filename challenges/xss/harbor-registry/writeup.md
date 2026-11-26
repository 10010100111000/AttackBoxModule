# Harbor Lights — Writeup

## 漏洞背景

本题基于真实 Django 1.11.4 的 CVE-2017-12794。漏洞位于 Django DEBUG 技术错误页面对异常信息的 HTML 渲染过程。特定异常内容未经正确的 HTML 上下文处理，可能导致反射型 XSS。

本题使用 PostgreSQL 的真实唯一约束冲突触发 Django ORM 的 `IntegrityError`，由原生 Django 1.11.4 错误页面提供漏洞上下文。没有自制 XSS 回显路由或模拟 traceback。

## 1. 侦察注册功能

访问 Harbor Registry 首页，发现公开用户名注册功能。正常注册一个用户名，观察响应。

再次提交相同用户名，应用会触发 PostgreSQL 唯一约束冲突。服务器返回 Django DEBUG 技术错误页面，而不是普通的业务错误页面。

## 2. 识别框架级 XSS

检查错误页面如何展示异常信息，并确认目标运行的是受影响的 Django 1.11.4。该问题并非应用主动把用户名输出到普通页面，而是框架在 DEBUG 错误页面中渲染异常内容时出现 HTML 上下文问题。

构造包含 HTML/JavaScript 的用户名输入，使其在真实错误页面上下文中执行。需要先完成注册，再重复提交相同内容，才能触发唯一约束异常。

## 3. 发现编辑部审核流程

浏览 Editorial submissions 页面，发现可以提交网站链接供编辑部审核。服务端将提交内容放入本地队列，由靶机内部的审核 Bot 处理。

Bot 使用独立的真实 Chromium 浏览器，并先登录 Django 应用的编辑部账户，再访问提交链接。它不会访问提交 URL 中的外部主机，而是保留路径并在本机应用源站打开。

## 4. 将 XSS 带入已认证浏览器

把构造好的注册错误页面 URL 作为网站地址提交到编辑部审核表单。

Bot 登录后访问该路径。由于目标页面来自同一个 Django 应用，注入脚本在已认证的编辑部浏览器会话中执行。

编辑部目标由 `/staff/flag` 提供，并通过 Django Session 中的 `is_editor` 状态进行访问控制。普通访客直接访问该路径会收到 HTTP 403。

## 5. 获取并提交 Flag

利用编辑部浏览器中的脚本请求同源的 `/staff/flag`，读取受保护的 Web 目标，再将响应发送到玩家控制的回调监听器。

提交回调中收到的 Flag。本题不需要读取容器文件、获得 Shell 或执行 Linux 提权。

## 漏洞链总结

1. 发现公开用户名注册。
2. 注册后重复提交相同用户名，触发真实 PostgreSQL 唯一约束异常。
3. 利用 Django 1.11.4 DEBUG 错误页面的反射型 XSS。
4. 发现编辑部链接审核流程。
5. 通过审核流程让已登录的真实 Chromium 访问构造的错误页面。
6. 在编辑部会话中请求受保护的 Web 目标。
7. 将 Flag 回传给玩家并提交。

## 关键源码位置

- `labs/django-debug-xss/app.py`：注册、重复用户名触发点、投稿流程和受保护目标。
- `labs/django-debug-xss/xss/models.py`：PostgreSQL 用户名唯一约束。
- `labs/django-debug-xss/bot.py`：编辑部登录、同源路径访问和真实 Chromium。
- `labs/django-debug-xss/seed.py`：每个实例的编辑部账户、Django Secret 和 Flag 初始化。
- 上游 Django 1.11.4：真实技术错误页面漏洞点。

## 参考资料

- Django 官方安全公告：https://www.djangoproject.com/weblog/2017/sep/05/security-releases/
- Vulhub CVE-2017-12794 复现：https://github.com/vulhub/vulhub/tree/master/django/CVE-2017-12794
- Django 1.11.5 修复版本说明：https://docs.djangoproject.com/en/1.11/releases/1.11.5/

本题保留真实 Django 框架漏洞和 PostgreSQL 触发机制。注册应用、编辑部审核 Bot 和 Flag 目标属于训练环境的业务封装，并非声称它们是原始 Vulhub 场景的一部分。
