# OpenAdmin — Writeup

## 目标

从 OpenNetAdmin 18.1.1 的网络诊断 AJAX 功能发现真实命令注入，读取 ONA 数据库配置并复用 jimmy 的 SSH 密码。通过 SSH 本地转发访问内部 PHP 应用，取得 Joanna 的加密私钥，最后利用 sudo 授权的 nano 取得 root。

## 1. 识别 OpenNetAdmin

访问网站的 /ona/ 路径，检查页面和版本信息，确认目标运行 OpenNetAdmin 18.1.1。继续浏览管理界面，留意网络诊断和 ping 功能。

## 2. 调查 xajax 网络诊断

检查页面请求与 xajax 调用，定位 window_submit 请求。上游 18.1.1 的 ws_ping() 函数将表单中的 IP 值拼接进 shell_exec() 的 ping 命令。

利用真实 xajax 请求验证服务器端命令执行，并确认执行身份为 www-data。随后读取 ONA 生成的数据库配置，发现数据库账户密码与 jimmy 的 SSH 密码相同。

## 3. 取得 jimmy 并访问内部服务

使用发现的凭据登录 SSH。检查 sshd 允许的转发配置，发现只允许访问 loopback 上的 52846 端口。

建立 SSH 本地转发，访问内部 Apache 虚拟主机。内部应用使用 SHA-512 密码哈希验证登录，登录后页面会读取并返回 Joanna 的加密 RSA 私钥。

## 4. 取得 Joanna 用户权限

使用公开线索验证内部应用的登录凭据，下载加密私钥。根据题目环境中的口令解锁私钥，并使用 SSH 公钥认证登录 Joanna。

确认身份后读取：

~~~sh
id
cat /home/joanna/user.txt
~~~

## 5. 利用 sudo nano 取得 root

检查 sudo 权限：

~~~sh
sudo -l
~~~

Joanna 可以免密执行 /bin/nano /opt/priv。nano 除了编辑文件，还提供读取文件和执行外部命令的交互功能。利用其命令执行功能取得 root 上下文，验证 UID 0 后读取：

~~~sh
cat /root/root.txt
~~~

## 攻击链总结

1. 识别 OpenNetAdmin 18.1.1。
2. 发现 xajax window_submit 调用原生 ws_ping()。
3. 利用 shell_exec() 命令注入取得 www-data。
4. 读取 ONA 数据库配置并恢复 jimmy SSH 凭据。
5. SSH 本地转发访问内部应用，取得 Joanna 加密私钥。
6. SSH 登录 Joanna，读取 User Flag。
7. 利用 sudo nano 的命令执行功能取得 root。
8. 读取 Root Flag。

## 复现边界

- OpenNetAdmin 18.1.1、xajax 与 ws_ping() 使用真实上游代码。
- ONA 数据库由上游安装器初始化。
- 内部 PHP 应用是基于公开行为独立重建，不声称是 HTB 未公开的原始源码。
- SSH、端口转发、加密私钥和 sudo nano 均使用真实系统组件。
