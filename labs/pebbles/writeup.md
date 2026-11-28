# PG Pebbles — Writeup

## 目标与复现边界

本 Lab 复现退役 OffSec Proving Grounds Pebbles 的 ZoneMinder SQL 注入与 MySQL UDF 权限链。ZoneMinder 1.29.0、MySQL 5.7、Apache/PHP、Tomcat、vsftpd 和 OpenSSH 使用真实组件。原题公开材料没有提供 Pebbles 首页的原始源码，因此首页按可观察行为重建；不声称与原版 HTML 完全一致。

原题的最终目标是读取 `/root/proof.txt`。本题不额外虚构 User Flag 阶段。

## 1. 端口枚举与服务识别

先扫描全部 TCP 端口，记录服务而不是只相信 Nmap 对非标准端口的默认服务名。预期可见：

- 21/tcp：vsftpd
- 22/tcp：OpenSSH
- 80/tcp：Apache/PHP，提供 Pebbles 登录页
- 3305/tcp：Apache，初始页面为 Ubuntu 默认页
- 8080/tcp：Apache Tomcat

3306/tcp 的 MySQL 和 8009/tcp 的 Tomcat AJP 不应从攻击者网络直接访问。

## 2. 浏览页面并发现 ZoneMinder

浏览 80 端口的登录页。它是侦察入口，不是本题的 SQL 注入点。继续检查 3305 端口，初始页面看起来只是 Apache 默认页。

对 Web 根目录进行目录枚举，在 3305 端口发现未链接的 `/zm/` 路径。访问后识别出 ZoneMinder Console，并确认版本为 1.29.0。8080 端口的 Tomcat 页面及其版本信息属于可见服务，但不是主要利用路径。

ZoneMinder 1.29.0 的上游日志处理代码将 POST 参数 `limit` 拼接到 SQL 查询中。该输入点对应 CVE-2016-10204 / Exploit-DB 41239。

## 3. 验证真实 SQL 注入

先在 ZoneMinder 的正常日志页面发起请求，并观察对应的 POST 参数：

- `view=request`
- `request=log`
- `task=query`
- `limit`

检查请求如何到达 `/zm/index.php`，再对 `limit` 进行受控测试。该注入支持堆叠查询；成功利用依赖真实 MariaDB/MySQL 执行后续语句，而不是应用层模拟的 SQLi 响应。

## 4. 利用数据库文件权限写入 PHP

数据库账户具有原题所需的全局文件权限。利用注入执行 `SELECT ... INTO OUTFILE`，将 PHP 内容写入 Apache 实际文档根目录，例如：

`/var/www/html/rce.php`

随后通过提供该文档的 HTTP 端口访问文件，确认 PHP 由 Apache 执行。命令以 Web 服务账户 `www-data` 运行。需要交互式访问时，可通过该 PHP 命令执行入口建立回连；这一步是 Web foothold，不是最终 Root Flag。

注意：80 与 3305 虽然都由 Apache 提供服务，但两个站点的文档根目录和访问路径不同。应通过实际响应确认新文件在哪个监听端口可访问，不要假设两个端口共享同一个站点根目录。

## 5. MySQL UDF 权限提升

本题保留原题危险的权限边界：MySQL 服务进程以容器内 UID 0 运行，ZoneMinder 数据库账户拥有 DBA 权限。通过本地枚举确认 MySQL 进程身份，并查询真实插件目录：

`SELECT @@plugin_dir;`

UDF 是 MySQL 的真实共享库扩展机制。攻击者需要将适用于目标 MySQL ABI 的 UDF 共享库送入目标容器；可以由攻击者控制的 HTTP 服务提供文件，再通过已取得的 `www-data` 命令执行能力下载到容器临时目录。不要把 CI 测试时由 Docker 主机复制进去的辅助库误认为玩家已有该文件。

随后继续利用同一个 ZoneMinder SQL 注入点完成数据库文件操作：

1. 创建用于暂存共享库字节的表。
2. 使用 `LOAD_FILE()` 读取临时目录中的 UDF 文件。
3. 使用 `SELECT ... INTO DUMPFILE` 将共享库写入实际 MySQL 插件目录。
4. 使用 `CREATE FUNCTION ... SONAME` 注册 UDF。
5. 调用 UDF 执行系统命令。

UDF 命令的执行身份取决于 MySQL 服务进程身份。本 Lab 中 MySQL 在容器内以 root 运行，因此 UDF 命令也以容器 UID 0 执行。

## 6. 读取 Root Flag

通过 UDF 执行读取：

`/root/proof.txt`

该文件权限限制为 root。Flag 是本题唯一的提交目标。

## 根因与修复建议

- 升级 ZoneMinder，并修复日志查询中将用户输入拼接进 SQL 的问题。
- 数据库账户不应拥有不必要的全局 DBA、FILE 或插件管理能力。
- MySQL 必须以专用、无特权的系统账户运行，不能以 root 启动。
- 限制 MySQL 插件目录的写入权限，审计 UDF 注册和加载行为。
- 数据库不应被允许向 Web 文档根目录写入可执行文件。

## 复现边界

- ZoneMinder 1.29.0 的漏洞代码来自上游原版软件包。
- Pebbles 首页是依据公开观察结果重建，不是原题未公开源码的逐字复刻。
- CI 使用独立构建的 UDF helper 验证 MySQL 插件加载与 UID 0 执行；测试环境通过 Docker 将 helper 放入临时容器。玩家路径则必须通过网络把真实 UDF 库送入目标，再利用 SQLi 写入插件目录。
- 生产环境必须注入私有静态 Root Flag；仓库中的 Flag 只是演示值。

## Sources

- ZoneMinder 1.29.0: https://github.com/ZoneMinder/zoneminder/tree/v1.29.0
- CVE-2016-10204: https://ubuntu.com/security/CVE-2016-10204
- Exploit-DB 41239: https://www.exploit-db.com/exploits/41239
- PG Pebbles walkthrough: https://www.juannemina.com/writeups/pebbles-proving-grounds/
- Additional walkthrough: https://pentesting.zeyu2001.com/proving-grounds/warm-up/pebbles
