# Trick — Writeup

## 范围与架构

本题保留 Trick 的 DNS → Payroll SQLi/FILE → Marketing PHP include → SSH → Fail2ban root action 主路径。它使用真实 BIND、Nginx、PHP-FPM、MariaDB、OpenSSH、Fail2ban 和 iptables，不模拟 DNS、SQL、文件读取或提权结果。

本平台重建版使用 Alpine 3.22 和 PHP 8.4 等较新运行环境，但保留原题可观察的漏洞行为、Linux 用户边界和权限配置。SMTP/mail-spool 备用路径不在本题范围内。

## 1. DNS 与虚拟主机枚举

先识别目标 IP 的反向 DNS，再尝试区域传送：

\`\`\`bash
dig -x <TARGET>
dig axfr trick.htb @<TARGET>
\`\`\`

AXFR 结果暴露 Payroll 子域。将域名加入本地 hosts 文件，或在请求中使用 Host header：

\`\`\`bash
curl -i -H 'Host: preprod-payroll.trick.htb' http://<TARGET>/
\`\`\`

主站、Payroll 和 Marketing 是三个不同的 Nginx 虚拟主机。Payroll 先通过 DNS 区域记录被发现，Marketing 则需要从后续应用行为中继续识别。

## 2. Payroll 登录 SQL Injection

观察登录表单提交到 \`POST /ajax.php?action=login\` 的请求。用户名会进入 MariaDB 查询字符串：

\`\`\`sql
SELECT * FROM users WHERE username = '<input>' AND password = '<password>'
\`\`\`

先比较普通无效用户名与逻辑表达式注入的响应：

\`\`\`text
username=' OR 1=1 -- -
\`\`\`

登录接口对成功与失败返回不同的数字响应。进一步利用 MariaDB 的真实 \`LOAD_FILE()\` 和 FILE 权限，通过条件表达式判断 Nginx 配置中是否包含某个字符串：

\`\`\`sql
' OR IF(LOCATE('preprod-marketing.trick.htb',LOAD_FILE('/etc/nginx/http.d/trick.conf'))>0,1,0)=1 -- -
\`\`\`

使用一个不存在的主机名构造负向条件，确认响应差异确实由文件内容判断产生，而不是固定回显。再检查 MariaDB 服务用户的文件权限边界：它不能读取 michael 的 mode-0600 SSH 私钥。

## 3. Marketing 的 nested traversal / LFI

访问 Marketing 虚拟主机，观察页面参数如何选择要 include 的文件。应用对路径做一次 \`str_replace('../', '', $file)\`，并将结果传给 PHP \`include()\`。

一次性替换并没有消除所有路径遍历形式。嵌套序列可以在替换后重新形成 \`../\`：

\`\`\`text
....//....//....//etc/passwd
\`\`\`

通过页面参数读取真实的 \`/etc/passwd\`，确认系统用户。随后读取 \`/proc/self/status\`，检查 Marketing PHP-FPM worker 的 UID 为 1001，即 michael。

在同一读取路径中访问 michael 的 SSH 私钥：

\`\`\`text
....//....//....//home/michael/.ssh/id_rsa
\`\`\`

将响应保存为本地私钥文件并设置 0600 权限。

## 4. SSH 立足点与 User Flag

使用读取到的真实私钥登录：

\`\`\`bash
ssh -i id_rsa michael@<TARGET>
\`\`\`

确认账户身份、组成员关系和用户 Flag：

\`\`\`bash
id
cat /home/michael/user.txt
\`\`\`

## 5. Fail2ban action 配置缺陷与 Root Flag

检查 sudo 权限：

\`\`\`bash
sudo -l
\`\`\`

michael 只能以 root 身份重启 Fail2ban 服务。继续检查 Fail2ban action 目录和 iptables-multiport action 文件的所有权、组权限及 include 关系。

该环境的 action 目录对 security 组可写，但 action 文件本身仍由 root 所有。可以在该目录中创建替换文件，再通过允许的服务重启使 Fail2ban 加载修改后的 action。

当 sshd jail 检测到同一来源的多次失败认证时，Fail2ban 会以 root 身份执行 actionban。重启前替换的 actionban 将 Root Flag 复制到一个 michael 可读的位置。等待短暂封禁结束后重新 SSH 登录并读取：

\`\`\`bash
cat /tmp/root.txt
\`\`\`

这条链验证的是 root 身份执行的真实 Fail2ban action；它并不意味着 michael 获得了持久 root shell。

## 自动化验收

\`labs/trick/tests/acceptance.py\` 是独立攻击端，按 DNS、HTTP、SSH 顺序完成完整链。CI 在内部 Docker 网络中运行目标与攻击端，目标仅获得其网络命名空间内所需的 NET_ADMIN capability。攻击端只访问 DNS、HTTP 和 SSH 服务，不挂载目标文件系统、不使用 Docker socket、不调用 \`docker exec\`。

CI 必须验证 User Flag 和 Root Flag 与当前随机 manifest/Challenge 答案逐字节一致。构建、healthcheck 或普通 HTTP smoke 单独通过不代表完整链通过。
