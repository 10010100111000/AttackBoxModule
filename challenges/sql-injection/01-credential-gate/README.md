# 暂停：PG Cockpit 原题研究尚不充分

> **不再制作 Credential Gate 原创登录演示。** 之前基于这个目录做过一个自编 Web 登录应用，并且已关闭未合并的 Draft PR #1，因为它没有复原真实 PG Cockpit。

已从第三方原题 Writeup 核对：

- 22/tcp OpenSSH 8.2p1。
- 80/tcp Apache 2.4.41，网站标题 **blaze**，其 PHP 登录页包含真实 MySQL SQLi；数据库为 blazeDB。
- 9090/tcp 是原生 Cockpit 管理平台，通过 SQLi 获得凭据后登录成为系统用户 james。
- 后续必须经过原题的自定义 SUID ELF `Authchecker` 的文件拷贝通配符漏洞，才能完成 Root。

**阻塞原因**：暂未取得可授权使用的 Blaze 自定义前端和 Authchecker 原始程序及完整代码。只搭一个自编登录页不足以称为“PG Cockpit 复现”。因此本题搁置，不能作为首个发布机器。

参考：https://hackindex.io/writeups/cockpit

首个正在研究的 SQLi 复现对象改为 [PG Pebbles（真实 ZoneMinder 1.29.0）](../../../labs/pebbles/RECONSTRUCTION.md)。当前使用静态 Flag；任何环境都必须先完成 Docker 真实利用链验收。
