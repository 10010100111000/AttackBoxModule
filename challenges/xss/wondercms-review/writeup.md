# Sea Glass — Writeup

## 目标与漏洞

本题使用真实 WonderCMS 3.4.2，复现 CVE-2023-41425 的反射型 XSS。漏洞位于登录页面将 `page` 参数反射到 HTML form 的 `action` 属性时，未正确处理属性上下文中的特殊字符。

题目把该漏洞放入一个真实的编辑投稿流程：访客提交网站地址，靶机内的管理员审阅 Bot 使用已登录的 WonderCMS 管理员浏览器访问该地址。利用反射型 XSS 后，可以在管理员会话上下文中访问受保护的审阅目标。

## 1. 侦察公开网站

浏览首页和 Submissions 页面，确认这是 WonderCMS 驱动的出版网站。查看 Contact 表单，发现访客可以提交姓名、邮箱、年龄、国家和网站地址。

表单成功提交后，网站会提示编辑团队将审核该网站。不要把提交成功误认为浏览器已经访问；需要继续理解后台审阅流程。

## 2. 确认 CMS 与登录页面

检查页面资源、响应头和公开路径，识别 WonderCMS 3.4.2。登录页面由 `index.php?page=loginURL` 提供。

原始 WonderCMS 3.4.2 在构造登录表单时，将 `page` 参数放入 HTML 属性上下文。对该参数进行适当编码后，可以结束原有属性/表单结构并插入 HTML 元素。

## 3. 构造反射型 XSS URL

利用属性上下文构造输入，核心结构如下：

```text
loginURL?"></form><script>/* JavaScript */</script><form action="
```

把它放入 `/index.php?page=` 参数并进行 URL 编码，形成提交给 Contact 表单的完整网站地址。

本题的审阅 Bot 会校验提交值是绝对 HTTP(S) URL，但随后丢弃其 authority，只取路径和查询部分，并在当前 WonderCMS 本机站点打开。因此，实际访问的是靶机内的 WonderCMS，而不是提交 URL 中指定的外部主机。

## 4. 利用管理员浏览器会话

Contact 表单将提交内容写入队列。靶机内的独立 Bot 读取队列，使用真实 Chromium Headless Shell 登录 WonderCMS 管理员账户，再访问刚才构造的路径。

在这个页面上下文中，注入脚本与 WonderCMS 同源，并继承管理员浏览器的 PHP Session。脚本可以请求：

```text
/review-proof.php
```

该页面不是漏洞模拟器，也不接受用户提供的 Flag 参数。它使用 WonderCMS 原生登录 Session 检查管理员身份，只有已登录管理员才能读取审阅目标。

## 5. 取回 Flag

脚本读取 `/review-proof.php` 的响应，并将内容发送到玩家控制的回调监听器。提交回调中收到的 Flag。

玩家不需要读取容器文件系统，也不需要获得管理员密码。Flag 位于受保护的 Web 审阅目标中，漏洞利用发生在真实管理员浏览器会话内。

## 漏洞链总结

1. 识别 WonderCMS 3.4.2。
2. 发现公开 Contact 投稿表单和管理员审阅流程。
3. 识别登录页面 `page` 参数的 HTML 属性上下文反射。
4. 构造反射型 XSS URL 并通过投稿表单提交。
5. 管理员 Bot 在真实 Chromium 中打开该 URL。
6. 利用管理员 Session 请求受保护的审阅目标。
7. 将 Flag 返回给玩家并提交。

## 关键源码位置

- 上游 WonderCMS：`labs/wondercms-xss` Dockerfile 固定的 3.4.2 commit。
- `labs/wondercms-xss/site/contact.php`：公开投稿表单和审阅队列。
- `labs/wondercms-xss/bot/review_bot.py`：管理员登录、同源路径访问和真实 Chromium。
- `labs/wondercms-xss/site/review-proof.php`：基于原生 WonderCMS Session 保护的 Web 目标。
- 上游 `index.php`：未修改的真实 CVE-2023-41425 漏洞点。

## 参考资料

- WonderCMS 3.4.2：https://github.com/WonderCMS/wondercms/releases/tag/3.4.2
- CVE-2023-41425：https://github.com/advisories/GHSA-58rr-37rr-r6h5
- 漏洞披露与 PoC：https://gist.github.com/prodigiousMind/fc69a79629c4ba9ee88a7ad526043413
- HTB Sea 公开 Writeup：https://0xdf.gitlab.io/2024/12/21/htb-sea.html

本题复现的是公开漏洞及管理员浏览器利用机制，不是原始 HTB Sea 镜像的逐字节复制。题目只覆盖 Web XSS 路径，不包含原机其他 Linux 利用和提权阶段。
