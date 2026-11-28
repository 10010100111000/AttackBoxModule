# Harbor Registry — Writeup

## 目标与组件

本 Lab 使用真实 Django 1.11.4（CVE-2017-12794）与 PostgreSQL。原始漏洞位于 Django 的 DEBUG 技术错误页面，不是自定义模板中的伪造反射点。社区资料库和编辑投稿流程是围绕漏洞构建的教学应用。

本题是 Web-only 路径，最终目标是编辑账户可读取的受保护 Flag，不要求 SSH 或 Linux 提权。

## 1. 侦察与正常注册

浏览首页，识别 Harbor Registry 的公开资料注册功能。页面要求用户提交公开昵称，并说明昵称必须唯一。继续检查 Editorial submissions 页面，发现访客可以提交网站链接，供编辑团队审阅。

先使用普通昵称注册一次，确认注册成功。再提交相同昵称，观察第二次请求的响应差异。

## 2. 触发真实 PostgreSQL 唯一约束异常

应用通过 Django ORM 创建用户记录：

`User.objects.create(username=request.GET['username'])`

PostgreSQL 对 username 的唯一约束会拒绝重复记录。第二次提交相同值时，数据库抛出真实 IntegrityError，Django 1.11.4 在 DEBUG 模式下生成技术错误页面。

Django 1.11.4 的错误页面对异常内容进行 HTML 渲染时存在 CVE-2017-12794。异常中包含请求提供的昵称，因此可以将脚本内容放入首次注册的昵称，再通过重复注册触发错误页面，让脚本在响应上下文中执行。

这个漏洞点来自未修改的受影响 Django 框架。题目没有增加一个专门回显输入的自定义 XSS 路由。

## 3. 理解编辑审阅流程

Editorial submissions 页面会把访客提交的 URL 放入本地审阅队列。容器内的 review bot 使用独立的非特权账户运行真实 Chromium，登录 Django 编辑账户，然后打开队列中的链接。

Bot 不会直接读取 Flag 文件。受保护的 `/staff/flag` 路由检查 Django Session 中的 `is_editor` 状态，只有已登录编辑会话可以读取 Flag。

## 4. 让编辑浏览器访问受控路径

构造能够触发 Django 技术错误页面的 URL，并把它提交到 Editorial submissions。Bot 对提交的绝对 URL 只提取路径和查询参数，丢弃外部 authority，然后在本机 Harbor Registry 来源下访问该路径。

因此，脚本在已登录编辑浏览器的同源上下文中执行，可以请求 `/staff/flag`。从匿名玩家直接访问该路径会得到 403；只有编辑会话可以读取内容。

## 5. 取回 Flag

注入脚本将受保护路由返回的 Flag 发送到玩家在同一私有练习网络中启动的 HTTP 回调监听器。玩家从自己的监听器取得 Flag，并提交到平台。

整个过程不需要读取目标容器文件、不需要知道编辑账户密码，也不需要 Worker 代替靶机读取 Flag 或执行判题。

## 漏洞根因与修复建议

- 将 Django 升级到修复版本。Django 1.11.5 修复了本题涉及的技术错误页面 XSS。
- 不要在生产环境启用 DEBUG。技术错误页面不应向外部用户展示完整异常上下文。
- 错误页面必须对所有用户可控数据进行正确的上下文编码。
- 管理员浏览器应限制对用户提交 URL 的访问，并采用隔离的浏览器配置文件与最小权限账户。
- 编辑专用 Flag 路由必须保留服务端身份验证，不能依赖隐藏链接或前端状态。

## 负向对照

仓库还保留 Django 1.11.5 的修复版本测试：重复昵称仍会触发 PostgreSQL 唯一约束错误，但相同输入不应在错误页面中执行 JavaScript。这样可以区分真实框架漏洞与普通数据库异常。

## Sources

- Django security release: https://www.djangoproject.com/weblog/2017/sep/05/security-releases/
- CVE-2017-12794 reproduction: https://github.com/vulhub/vulhub/tree/master/django/CVE-2017-12794
