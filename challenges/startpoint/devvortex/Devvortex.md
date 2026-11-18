---
summary: 某科技公司正在开发新的技术门户与内部管理系统。你需要通过虚拟主机枚举突破外围，并利用已知 CMS 缺陷与特权程序漏洞逐步提权夺取整机最高控制权。
level: medium
lab: devvortex
---

# 场景

某科技公司正在开发新的技术门户与内部管理系统。你需要通过虚拟主机枚举突破外围，并利用已知 CMS 缺陷与特权程序漏洞逐步提权夺取整机最高控制权。

# 任务

探测目标主机开放服务与虚拟主机配置，利用 CMS 历史安全漏洞获取系统初始立足点；搜集系统内部凭据横向移动，并利用本地提权漏洞获取系统最高控制权。

```quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  通过 Host 头虚拟主机枚举发现开发站点，利用 Joomla 4.2.6 信息泄露缺陷获取数据库及后台管理员凭据。登录后台获取 WebShell 突破边界，并进一步提取账户凭据通过 SSH 登录目标主机，提交 `/home/logan/user.txt` 中的 Flag。
answer: "DEVVORTEX{local_user_flag_demo}"
match: trim
hint: 枚举 dev.devvortex.htb 虚拟主机，审计 /api/index.php/v1/config/application 接口。
```

```quiz
title: 获取最高权限 (Root Flag)
kind: flag
prompt: |
  检查用户 logan 在主机上的 sudo 特权，利用未修复的 Apport 提权缺陷接管系统，读取 `/root/root.txt` 中的 Flag 并提交。
answer: "DEVVORTEX{local_root_flag_demo}"
match: trim
hint: 检查 sudo -l 与 apport-cli 的版本及调用行为。
```
