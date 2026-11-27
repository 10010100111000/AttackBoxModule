# BountyHunter — Writeup

## 目标

从公开的漏洞悬赏门户发现 beta 报告系统，追踪浏览器提交的 base64 XML，利用真实 PHP SimpleXML/libxml 外部实体解析读取 db.php 配置。使用配置中的 development 凭据通过 SSH 取得初始访问，再检查 sudo 授权的 Skytrain 票据验证器，利用真实 Python eval 取得 root。

## 1. 侦察公开门户

访问首页，识别 Bounty Hunters 漏洞悬赏页面。Portal 页面提示报告系统仍在开发中，继续进入报告表单并检查页面源码及加载的 JavaScript。

bountylog.js 会将用户输入拼接为 XML，再对 XML 进行 base64 编码，通过 POST 请求提交给 tracker_diRbPr00f314.php。这里应以实际请求为准，而不是只观察表单字段。

## 2. 检查 XML 解析器

提交一份普通报告，确认后台能够解析并返回 title、CWE、CVSS 与 reward 字段。

随后检查服务端对 XML 外部实体的处理。tracker 使用 PHP SimpleXML/libxml，并启用了实体替换。构造外部实体引用，利用 PHP stream filter 读取 db.php 的源码，再从返回的 Base64 内容中提取测试凭据。

这是真实 PHP/libxml 与 PHP stream wrapper 的组合行为，不是自定义文件读取接口。

## 3. 取得 development SSH 访问

使用读取到的配置凭据登录 development 账户：

~~~sh
id
sudo -l
~~~

确认账户能够读取 User Flag，但不能直接读取 /root/root.txt。随后检查 sudoers 对 Skytrain ticketValidator.py 的精确授权。

## 4. 分析 Skytrain 票据验证器

检查 /opt/skytrain_inc/ticketValidator.py。验证器会读取 Markdown 票据，从 Ticket Code 中提取编号并检查其模 7 结果，之后对票据表达式调用 Python eval。

票据编号检查并不能约束后续表达式的副作用。构造满足编号条件且总额大于 100 的表达式，使 eval 在 sudo 提供的 root 上下文中执行系统命令。

## 5. 取得 Root Flag

通过 sudo 执行真实票据验证脚本，利用表达式求值在 root 上下文中读取 /root/root.txt，并提交 Root Flag。

## 攻击链总结

1. 访问公开门户并发现 beta 报告系统。
2. 检查 bountylog.js，确认 base64 XML 提交流程。
3. 利用 PHP SimpleXML/libxml XXE 与 php://filter 读取 db.php。
4. 恢复凭据并通过 SSH 登录 development。
5. 检查 sudo 授权的 Skytrain ticketValidator.py。
6. 利用 Python eval 在 root 上下文中执行代码。
7. 读取 Root Flag。

## 复现边界

- PHP 使用真实 SimpleXML/libxml 与 LIBXML_NOENT。
- 外部实体通过真实 php://filter stream wrapper 读取应用配置。
- SSH 使用真实 OpenSSH 密码认证。
- sudoers 只授权指定 Python 脚本；提权来自该脚本真实的 eval 行为。
- 原始 HTB 网站源码未公开；门户页面和 beta 流程按公开 writeup 独立重建。
- 不使用模拟 XML 解析、伪造 SSH 服务或自定义 root 命令接口。
