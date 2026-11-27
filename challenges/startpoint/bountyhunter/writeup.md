# BountyHunter — Writeup

## 目标

从漏洞悬赏门户的报告提交流程发现真实 PHP/libxml XXE，读取 PHP 配置文件并恢复 development 的 SSH 凭据。登录后检查 sudo 授权的 Skytrain 票据验证程序，利用其真实 Python eval 行为取得 root。

## 1. 侦察公开网站

浏览首页、Portal 与报告提交页面。首页没有直接说明后台解析器的实现细节。查看报告页面加载的 JavaScript，确认浏览器会将结构化 XML 编码后提交给后台 tracker。

先提交普通 XML 报告，观察服务器返回的字段回显。这一步用于确定报告内容的正常处理路径。

## 2. 调查 XML 解析器

检查报告数据如何传入 PHP。后台使用 SimpleXML/libxml 并启用了实体替换。构造 XML 外部实体，令解析器读取服务器本地文件。

先读取无敏感信息的系统文件确认文件实体解析行为，再进一步读取站点配置文件，恢复 development 账户复用的凭据。

## 3. 取得 development 账户

使用恢复的凭据通过 SSH 登录。确认身份并读取 User Flag：

~~~sh
id
cat /home/development/user.txt
~~~

随后检查 sudo 权限，确认当前账户可以免密执行指定的 Skytrain Python 验证程序。

## 4. 分析 Skytrain 票据验证器

检查 /opt/skytrain_inc/ticketValidator.py。程序先检查 Markdown 票据的格式和编号，再将票据代码交给 Python eval() 计算。

eval() 会在当前 Python 进程的权限上下文中执行表达式。由于程序由 sudo 以 root 身份启动，票据中的表达式也会以 root 身份执行。

## 5. 通过真实 eval 行为取得 Root

构造满足票据格式与编号检查的 Markdown 文件，使验证器在 eval() 中执行系统命令。确认执行身份为 UID 0，并读取 /root/root.txt。

CI 使用真实 SSH 登录和原始票据验证器完成该路径，不调用测试专用提权接口，也不直接以 root 身份执行票据内容。

## 攻击链总结

1. 公开网站侦察与正常报告提交。
2. 发现客户端提交的 XML 数据进入真实 PHP SimpleXML/libxml。
3. 利用外部实体读取 PHP 配置并恢复 development 凭据。
4. SSH 登录 development，读取 User Flag。
5. 检查 sudo，发现被授权执行 Skytrain ticketValidator.py。
6. 利用真实 Python eval() 在 root 上下文中执行命令。
7. 读取 Root Flag。

## 复现边界

- Apache/PHP 使用原生 SimpleXML/libxml 与真实外部实体解析。
- SSH 使用系统 OpenSSH 与实际 development 账户。
- sudo 使用系统原生 sudoers。
- Skytrain 验证器为真实 Python 程序，其危险行为来自 eval()，不是模拟执行接口。
- 原始 HTB 站点源码未公开；页面与报告流程为根据公开观察独立重建。
