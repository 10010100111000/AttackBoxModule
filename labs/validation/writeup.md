# Validation — Writeup

## 目标与复现边界

本 Lab 根据退役 HTB Validation 的公开资料独立重建。原始 PHP 应用源码没有公开，因此注册页、账户页与路由行为是依据公开 Writeup 重建；漏洞仍由真实 PHP、MariaDB、Unix 文件权限、PHP-FPM 与系统 `su` 认证实现。

本 Lab 使用两个提交目标：`/home/htb/user.txt` 与 `/root/root.txt`。生产环境必须通过现有 Worker 环境变量注入私有 Flag；仓库中的答案仅为演示种子。

## 1. 侦察与正常注册

扫描目标，识别 HTTP 80 与 OpenSSH 22。浏览 HTTP 首页，看到 UHC September Qualifiers 的注册表单。正常业务流程只要求用户名与国家，不会直接暴露 SQL 查询或管理接口。

提交一组普通注册信息。应用执行以下步骤：

1. 接收 username 与 country。
2. 计算用户名的 MD5 值，作为用户 Cookie。
3. 使用参数化 INSERT 将用户名、哈希、国家和注册时间写入 MariaDB。
4. 设置名为 `user` 的 Cookie，并重定向到账户页面。

这一步的 INSERT 使用 prepared statement，本身不是注入点。

## 2. 找到二阶 SQL 注入

账户页面读取 Cookie 对应的注册记录。它先使用参数化查询取得当前用户的 username 与 country，然后把数据库中保存的 country 值拼接到另一条 SQL 查询：

`SELECT username FROM registration WHERE country = '<stored country>'`

因此，注入发生在第二次使用数据时：注册阶段保存的输入在后续请求中被当作 SQL 语法执行。这是二阶 SQL 注入，而不是简单地把恶意参数直接放进同一次查询。

通过 UNION 查询控制结果列，并观察页面参赛者列表中的回显。进一步枚举数据库上下文，确认当前数据库账户具有 MariaDB 的 FILE 权限。

## 3. 通过 LOAD_FILE 读取应用配置

利用真实的 `LOAD_FILE()` 读取非敏感系统文件，确认数据库文件读取能力。随后读取 PHP 运行时配置文件：

`/var/www/html/config.php`

配置文件不会被 Web 服务器直接当作源码返回，因为 PHP-FPM 正常执行它；但 MariaDB 的 FILE 权限可以读取其磁盘内容，并将查询结果通过账户页面回显。

配置中包含数据库账户密码。该密码同时被复用于 Linux root 账户的密码认证。这是本题从 Web 数据访问转向系统身份验证的关键转折。

## 4. 通过 INTO OUTFILE 写入 PHP

MariaDB 服务账户对 Web 文档根目录具有写入权限。利用 `SELECT ... INTO OUTFILE` 将 PHP 内容写入：

`/var/www/html/<chosen-name>.php`

通过 HTTP 访问该文件，确认 Apache 将其交给真实 PHP-FPM 解释。命令以 Apache Web 账户身份执行。此时可以读取权限允许访问的：

`/home/htb/user.txt`

取得 User Flag。

## 5. 利用凭据复用与原生 su

从 PHP 命令执行能力调用系统 `su`，使用配置文件中恢复的密码进行 root 身份验证。这里使用的是 Linux 原生密码认证与真实 setuid `su` 程序，不是 sudo 规则、伪造接口或模拟提权脚本。

在取得 root shell 后读取：

`/root/root.txt`

取得 Root Flag。

## 根因与修复建议

- 二阶 SQL 注入的根因是：写入阶段使用参数化查询，但后续读取阶段又把已存储数据拼接进 SQL。所有 SQL 查询都必须参数化，不能只保护 INSERT。
- 数据库账户不应拥有全局 FILE 权限；限制 `LOAD_FILE` 与 `INTO OUTFILE`，并将 `secure_file_priv` 设置为受限目录。
- 数据库服务账户不应对 Web 文档根目录拥有写权限。
- Web 应用配置不得保存可复用于系统账户的密码；数据库凭据与 Unix 登录凭据必须分离。
- 不应允许 Web 服务账户通过可复用的密码进入 root 身份验证流程。

## 复现边界

- 原始 HTB PHP 源码未公开；站点结构和业务流程依据公开资料重建。
- SQL 注入、MariaDB FILE 操作、PHP 执行、Unix 密码认证和 `su` 均使用真实组件。
- 当前历史 CI 已验证注册流程、二阶 SQLi、LOAD_FILE、配置读取、INTO OUTFILE 与原生 su 认证的组件行为；尚未建立当前统一标准下的独立网络攻击者完整链 E2E。
- Worker 部署与生产资源验收不属于本次 Challenge 文档集成。

## Sources

- https://pencer.io/ctf/ctf-htb-validation/
- https://fahmifj.github.io/ctf/hackthebox/validation/
- https://0xdf.gitlab.io/2021/09/14/htb-validation.html
