# OpenAdmin — Writeup

## 目标与复现边界

本 Lab 使用真实 OpenNetAdmin 18.1.1、其原版 xajax 库与 PHP 处理代码。公开原题内部 PHP 应用的完整源码不可得，因此内网应用的登录页、密码校验和私钥展示行为是依据公开 Writeup 重建；不声称其为 HTB 原始源码。

## 1. 侦察与版本识别

扫描目标，确认 HTTP 80 与 SSH 22。浏览站点并访问 /ona/，识别 OpenNetAdmin 18.1.1。检查应用提供的网络诊断功能，留意 xajax 请求如何提交诊断参数。

## 2. 原生 xajax 命令注入

OpenNetAdmin 18.1.1 的 www/winc/tooltips.inc.php 中，ws_ping() 将用户提供的 IP 参数拼接到 shell_exec() 的 ping 命令中。未认证的 xajax window_submit 请求可以到达该处理函数。

利用该真实请求路径执行受控命令，确认初始命令执行身份为 Apache 的 www-data。这不是额外添加的模拟命令接口。

## 3. 数据库凭据复用与 Jimmy SSH

检查 ONA 安装时生成的配置文件：/opt/ona/www/local/config/database_settings.inc.php。该文件包含真实 MySQL 数据库账户 ona_sys 的凭据。该密码与系统账户 jimmy 的 SSH 密码复用。

使用发现的凭据通过原生 OpenSSH 登录 Jimmy。这里的凭据转折来自 ONA 实际安装配置，不是测试容器注入的额外账户接口。

## 4. SSH 隧道与内部 PHP 应用

枚举 Jimmy 可访问的本机监听服务，发现 Apache 内部应用绑定在 127.0.0.1:52846。通过 SSH 本地端口转发访问该服务。

内部应用的登录页使用 Jimmy 的口令 Revealed。登录后进入 main.php，页面会展示 Joanna 的加密 RSA 私钥。该小型内部应用是基于公开 Writeup 对未公开原始应用行为的明确重建。

保存私钥后，识别其加密口令为 bloodninjas，使用该私钥通过 SSH 登录 Joanna，并读取 /home/joanna/user.txt，取得 User Flag。

## 5. sudo nano 权限提升

以 Joanna 身份检查 sudo 授权，发现允许免密运行 /bin/nano /opt/priv。该授权限制了被打开的文件路径，却没有限制 nano 自身的交互式功能。nano 提供读取文件和执行外部命令的快捷键；利用其命令执行提示可以在 sudo 提供的 root 权限上下文中启动 shell，再读取 /root/root.txt，取得 Root Flag。

## 根因与修复建议

- 升级 OpenNetAdmin，并修复 xajax 网络诊断参数进入 shell 命令的注入点。
- 不要在 Web 可读配置中保存可复用于系统 SSH 账户的密码。
- 内部管理应用应使用独立凭据，并避免向普通用户展示其他账户的私钥。
- 不要直接 sudo 授权交互式编辑器。需要维护受保护文件时，应提供参数固定、功能受限的专用程序或脚本。

## 复现与验证边界

- ONA 18.1.1、xajax、ws_ping()、MySQL、Apache、OpenSSH 和 nano 均为真实组件。
- 内部 PHP 应用按公开证据重建，不是 HTB 未公开源代码的逐字复刻。
- 当前 CI 的独立攻击端已验证至 Joanna 并取得准确 User Flag。Root 阶段的 Expect 脚本固定读取 /tmp/joanna_id_rsa，而攻击端实际将私钥放在临时目录并作为参数传入；脚本忽略该参数，因此这次 CI 没有完成 Root 证明。
- 该失败定位在测试脚本路径衔接，不是已经证实 nano 提权不可用。根据真实 sudoers 规则与 nano 的原生交互式命令功能，Root 路径具备可行条件。本项目决定不为这个测试脚本路径问题继续重跑 E2E；因此 Catalog 保留 pending，不虚报本次完整 E2E 通过。

## Sources

- OpenNetAdmin 18.1.1: https://github.com/opennetadmin/ona/tree/v18.1.1
- Original xajax RCE PoC: https://github.com/amriunix/ona-rce
- https://hackindex.io/writeups/openadmin
- https://h4ckron.github.io/htb-writeup-openadmin/
- https://moisestapia.github.io/htb-writeup-openadmin/
