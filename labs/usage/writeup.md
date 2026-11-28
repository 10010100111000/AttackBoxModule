# Usage — Writeup

## 目标与复现边界

本 Lab 根据退役 HTB Usage 的公开资料独立重建。原始 HTB 应用源码未公开，因此 Daily Blogs 的主要路由和页面依据公开 Writeup 重建；漏洞使用真实 Laravel 10.18.0、MySQL 8.0.46、Laravel-admin 1.8.19、PHP-FPM、OpenSSH、Monit、sudo 与 p7zip 16.02。

原题私有的 `usage_management` helper 无法获得。本复现明确使用真实 p7zip 16.02 的 `@listfile` 行为完成 Root 阶段，不声称恢复了原始 helper。

## 1. 侦察与账户注册

将目标 IP 映射到 `usage.htb` 与 `admin.usage.htb`，检查 HTTP 服务和虚拟主机。浏览 Daily Blogs 首页，注册普通账户并熟悉正常页面。

继续检查密码恢复流程。表单提交邮箱地址，使用 Laravel 正常的 CSRF 与 Session 机制。

## 2. 密码恢复中的布尔与时间盲注

对 `POST /forget-password` 的 `email` 参数进行受控比较，观察真/假条件造成的响应差异。进一步比较包含 MySQL `SLEEP()` 条件的请求，确认时间型响应差异。

应用使用真实 Laravel 查询路径与 MySQL 数据库，不使用模拟 SQL 解析器。通过布尔和时间信号恢复后台管理员账户的真实 remember_token。该字段是 Laravel-admin 原生持久登录令牌，本版本将 Blind Recovery 的 Flag 作为该管理员记录的持久登录令牌；同时继续提取 bcrypt 密码哈希并在本地离线进行密码恢复。数据库 Flag 不通过额外的伪造接口返回。

## 3. 取得数据库 Flag 并登录真实 Laravel-admin 后台

将提取出的 admin_users.remember_token 与 Blind Recovery Challenge 的答案比较，即完成 SQLi 专项目标。随后使用恢复的 bcrypt 密码登录真实后台，继续完整链。该字段来自 Laravel-admin 上游迁移定义的原生 remember token 列，而不是额外创建的 flag 表。



使用恢复的管理员凭据访问 `admin.usage.htb/auth/login`。后台由真实 `encore/laravel-admin 1.8.19` 软件包提供，而不是自制的仿冒上传页面。

进入账户设置，检查头像 Image 字段。该版本的上传处理存在文件类型与内容校验缺陷，可接受特制的图片/PHP polyglot，并以原始文件名保存到公开上传目录。

## 4. 通过头像上传取得 dash

利用真实头像上传处理，将可执行的 PHP 内容保存到公开上传路径。通过 HTTP 请求访问上传文件，确认 PHP-FPM 以 `dash` 用户执行。

在该执行上下文中读取 `/home/dash/user.txt`，取得 User Flag；同时检查 `dash` 的 SSH 私钥和 Monit 配置文件。

## 5. 从 dash 转向 xander

使用从 Web foothold 获得的 SSH 私钥登录 `dash`。检查 `/home/dash/.monitrc`，发现 Monit 管理凭据与系统用户 `xander` 的密码复用。

使用该凭据通过 SSH 登录 xander。继续检查 sudo 授权，发现允许执行真实 `/usr/bin/7za` 的归档命令。

## 6. 利用 p7zip @listfile 读取 Root Flag

目标使用 p7zip 16.02。该版本会把以 `@` 开头的归档参数解释为文件列表输入。结合 sudo 允许的固定归档命令与文件名/列表文件解析行为，可以让高权限归档程序读取攻击者控制的列表内容，并访问 root-only 文件。

最终读取：

`/root/root.txt`

取得 Root Flag。

## 根因与修复建议

- 密码恢复流程应使用参数化查询，避免将邮箱输入拼接进 SQL。
- 对布尔和时间盲注应使用统一的输入校验与安全查询构造，不能仅依赖响应文案隐藏结果。
- 升级受影响的 Laravel-admin 版本，并对上传文件执行服务端 MIME、内容和扩展名校验；将上传内容存放在不可执行目录。
- 管理员密码、数据库凭据、Monit 凭据与 Unix 登录密码必须彼此独立。
- sudo 不应授权对复杂归档工具的宽泛参数组合；需要备份时应使用固定脚本、固定目录和严格白名单。
- 升级 p7zip，并避免让高权限工具解析用户可控的 listfile。

## 复现边界

- Daily Blogs 的原始私有源码不可得，主应用路由和 UI 是根据公开材料重建。
- Laravel-admin 1.8.19、MySQL 8.0.46、PHP-FPM、OpenSSH、Monit、sudo 和 p7zip 16.02 均为真实组件。
- Root 阶段使用 p7zip 的真实 `@listfile` 解析行为，是对不可获得的原题私有 helper 的明确适配。
- 历史完整链 CI 已验证该路径与两实例重置；当前统一 E2E 状态仍需按 Catalog 单独记录。
- 生产环境必须由 Worker 注入私有 User/Root Flag，Challenge 答案必须与注入值一致。

## Sources

- HTB Usage: https://www.hackthebox.com/machines/usage
- IppSec: https://www.youtube.com/watch?v=cx9Da-PoXG4
- https://www.cipherbuu.net/posts/Usage-Walkthrough/
- https://www.brunorochamoura.com/posts/usage/
- Laravel-admin CVE-2023-24249: https://github.com/advisories/GHSA-58rr-37rr-r6h5
- Vulnerable Laravel-admin source: https://github.com/z-song/laravel-admin/commit/6c292ebb5efa886fa4776d86e975180608505946
