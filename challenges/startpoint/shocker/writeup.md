# Shocker — Writeup

## 目标

通过公开 Web 服务发现未链接的 Apache CGI 脚本，识别其使用的旧版 GNU Bash，并利用 Shellshock（CVE-2014-6271）取得 shelly 用户的执行权限。随后审计 sudoers 配置，利用被授权的 Perl 解释器读取 Root Flag。

## 1. 侦察服务

先枚举目标开放端口，确认 HTTP 服务与 SSH 服务。访问网站首页，观察页面内容和 HTML 源码。首页没有直接暴露后台脚本位置，因此需要继续检查 Web 服务器常见目录和资源。

## 2. 发现 CGI 脚本

检查服务器的 CGI 目录与脚本扩展名。发现一个用于输出系统运行时间的脚本。直接访问时，脚本正常返回 uptime 信息。

从响应头、脚本行为与服务配置入手，判断该脚本由 Bash 解释器执行。关键问题在于 CGI 会将 HTTP 请求头转换为进程环境变量，而旧版 Bash 对函数定义环境变量的解析存在缺陷。

## 3. 利用 Shellshock

CVE-2014-6271 影响存在漏洞的 Bash 版本。构造 HTTP 请求头，使 Apache CGI 将其作为环境变量传入 Bash。易受影响的 Bash 在解析环境变量时会继续执行函数定义之后的命令。

在真实 Apache CGI 与 Bash 4.3 环境中执行命令，确认身份为 shelly，并读取 User Flag：

~~~sh
id
cat /home/shelly/user.txt
~~~

这里使用的是上游 Bash 4.3 的真实漏洞行为，不是应用层对特定字符串的匹配或模拟命令执行。

## 4. 检查 sudo 权限

取得 shelly 的执行权限后，检查 sudoers：

~~~sh
sudo -l
~~~

配置允许该账户免密执行 /usr/bin/perl。Perl 不只是一个固定功能的管理命令；它支持执行任意 Perl 程序。因此，这项授权实际上允许调用者以 root 身份运行任意 Perl 代码。

## 5. 通过 Perl 读取 Root Flag

利用被授权的 Perl 解释器在 root 上下文中访问 /root/root.txt，取得并提交 Root Flag。

## 攻击链总结

1. 枚举 HTTP 与 SSH 服务。
2. 从普通网站继续发现未链接的 CGI 脚本。
3. 确认 CGI 使用 GNU Bash 4.3。
4. 利用 CVE-2014-6271 执行命令并取得 shelly 身份。
5. 读取 User Flag。
6. 检查 sudoers，发现免密执行 Perl 的授权。
7. 利用 Perl 的程序执行能力取得 root 上下文并读取 Root Flag。

## 复现边界

- GNU Bash 4.3 使用官方上游源码构建，并校验归档 SHA-256。
- Apache 使用原生 mod_cgi 执行真实 shell 脚本。
- Shellshock 通过实际 HTTP 请求头进入 CGI 环境变量。
- sudo 使用系统原生 sudoers 规则与真实 Perl 解释器。
- 首页外观为独立重制；不声称拥有 HTB 未公开的原始首页素材。
