# PG Pebbles — 原题优先的复现与验收记录

> **状态：原版 ZoneMinder Docker 镜像及核心漏洞链已通过 GitHub Actions 实测；还未通过实际 Worker 节点验收，未发布。**
>
> 目标不是另写一个带 SQLi 的网站，而是尽可能复原 OffSec PG Practice *Pebbles* 的真实服务、访问入口、前端和权限转折。公开资料无法还原的部分必须注明，不应编造并宣称与原题一致。

## 1. 已核对的原题环境

| 原题端口 | 观察到的服务 | 玩家可见内容与作用 | 已知软件 |
| --- | --- | --- | --- |
| TCP/21 | FTP | 枚举入口之一，非主要利用路径 | vsftpd 3.0.3 |
| TCP/22 | SSH | 枚举入口之一 | OpenSSH 7.2p2 (Ubuntu) |
| TCP/80 | HTTP | Pebbles 自定义登录页；多份独立 Writeup 确认该端口的未链接 /zm 可通过目录枚举发现 | Apache 2.4.18、PHP（原自定义代码**未知**） |
| TCP/3305 | HTTP | 初始 Apache 默认页；枚举发现 /zm/ 的真正 ZoneMinder 控制台 | Apache 2.4.18 + ZoneMinder 1.29.0 |
| TCP/8080 | HTTP | Tomcat 9.0.30 页面与干扰性路径（不同 Writeup 对实际后端与路径记录有所差异） | Apache Tomcat 9.0.30 |

- 操作系统：Writeup 中显示 Ubuntu 16.04.6；Docker 内必须测试镜像兼容性，不能假称与完整 Ubuntu 主机相同。
- 前端：**优先直接使用 ZoneMinder v1.29.0 原版 Web 前端、CSS、JavaScript 和管理界面**，而非写一套长得差不多的页面。
- 后端：ZoneMinder 自身 PHP/Perl 服务、MySQL 5.7.30。
- 权限模型：原题 MySQL 以 OS root 身份运行，并允许数据库文件写入和加载 UDF。这是原题能够 Root 的关键配置，不是 SQLi 自带的权限。
- 原题未公开的 Pebbles 首页源码及其他私有组件，暂不声称可以一比一复制。

## 2. 玩家应当如何发现

1. 对目标 IP 进行端口扫描，得到 FTP、SSH、80/3305/8080 上的 HTTP。
2. 浏览多个 HTTP 首页，发现普通登录页、默认 Apache 页面、Tomcat 页面，不能在首页直接展示“SQL 注入”提示。
3. 对 3305 端口进行路径枚举，从普通默认页面发现 **/zm/**。
4. 在原版 ZoneMinder Web 界面识别 1.29.0，再研究对应历史版本的公开漏洞。
5. 在应用真实的日志查询功能中确认 POST `limit` SQL 注入，不能用 payload 字符串匹配的假接口代替。
6. 理解 SQL 权限后，通过数据库向 Apache Web 根目录写文件，得到以 `www-data` 运行的 PHP 执行能力。
7. 在获得低权限系统访问后，识别 MySQL 服务以 root 运行以及其 UDF/plugin 权限，独立完成容器内 Root。
8. 取得静态 Flag；原题报告主要记载 `/root/proof.txt`，暂不凭空增加必需的 User Flag。

## 3. 可核实的原始材料

- **原版软件**：https://github.com/ZoneMinder/zoneminder/tree/v1.29.0
- 上游 Git tag `v1.29.0` 指向 commit `6de2ab504c71217fa3797b9d041199795c3ca804`（已从 GitHub API 核对）。
- 上游旧版本 Ubuntu 16.04 安装指引：https://wiki.zoneminder.com/Ubuntu_Server_16.04_64-bit_with_Zoneminder_1.29.0_the_easy_way
- 原版漏洞报告：Exploit-DB 41239（ZoneMinder 1.29/1.30 `limit` SQL injection），https://www.exploit-db.com/exploits/41239
- 完整 PG 第三方 Writeup：https://www.juannemina.com/writeups/pebbles-proving-grounds/
- 更多原题记录：https://pentesting.zeyu2001.com/proving-grounds/warm-up/pebbles
- ZoneMinder 许可证：上游 GitHub 标注 GPL-2.0；保留上游许可证与来源，不导入未授权的 OffSec 原题资源。

## 4. Docker 平台适配

已核对 `attackbox/worker/node/targets/model.go` 与 `engine.go`：

- 当前 Worker 以**单个 Docker 容器**作为一个靶机实例，用户通过隔离目标网络访问其 IP；并不支持一题自动创建多个 Compose 容器。
- 因此原题涉及的真实 Apache、PHP、MySQL、Tomcat、FTP、SSH 服务，需在同一容器内使用原进程运行，保留独立端口；进程监管可作为启动实现，不改变应用本身。
- Docker 默认资源配置是 512 MiB / 1 CPU / 256 PIDs。CI 曾在此限额下健康运行，内存快照约 418.8 MiB、100 PIDs，但未做压力测试；建议上线前在真实 Worker 节点以 1 GiB 测试，勿将 CI 单次采样视为稳定并发容量。
- 原题 MySQL 的 root 运行及 UDF 执行只允许在隔离 Docker 实例内部；禁止 privileged、宿主机根目录或 Docker socket 挂载，不能以宿主级提权替代真实利用链。
- 所有故意脆弱端口只可通过平台的私有练习网络访问，不得在公网直连暴露。
- 按项目现状暂用**静态 Flag**；与现有 `quiz.answer` 一致，无需先改造动态 Flag 服务端。

## 5. 当前实测验收（2026-11-22 核查）

原始整栈的 GitHub Actions 成功运行：[44943603262](https://github.com/10010100111000/AttackBoxModule/actions/runs/44943603262)。验证对象是独立 Linux Docker 容器与另一台 Docker 攻击者容器；不是生产 Worker 节点。

| 验收项 | 现状与证据边界 |
| --- | --- |
| Ubuntu 16.04、ZoneMinder 1.29.0、MySQL 5.7、Apache/PHP、Tomcat、FTP、SSH | **CI 已构建成功**；使用真实上游包和签名校验 |
| TCP 21/22/80/3305/8080 可枚举，数据库及 AJP 不对外 | **独立攻击容器验收通过**，FTP banner 恢复正常 |
| PHP 登录首页没有直接暗示漏洞，/zm 可被目录枚举找到 | **HTTP 黑盒检查通过**；80 端口自定义页面仍是行为近似，并非原版 HTML/CSS |
| ZoneMinder 1.29.0 原始 PHP SQLi | **真实 SQLi HTTP 请求、文件写入及 Apache PHP 执行通过** |
| MySQL UDF → UID 0 → 读取容器 Root proof | **独立 CI UDF helper 测试通过**；helper 仅用于验证，不进入正式靶机镜像 |
| 512 MiB 默认资源配置 | **CI 短暂健康运行**：内存约 418.8 MiB / 512 MiB、100 PIDs；并发与峰值未实测 |
| 静态 Flag、删除新建后重置数据库/文件状态 | 静态演示 Flag 可用；**专门的重启、重建验收脚本已添加，尚待最新 CI 结果** |
| 真实 Worker 网络、宿主隔离、并发用户、发布 | **未验证**，不得宣称正式上线 |

历史 Ubuntu 包、ZoneMinder 原版源码和漏洞均已通过 CI；剩余重点是**实例生命周期、原版页面差异和生产 Worker 隔离**。不可使用特权容器、宿主目录或 Docker socket 来缩短验证链。

## 6. 选题决策

此前的 `Credential Gate` 是原创演示程序，不属于 PG Cockpit 的复现。原 PG Cockpit 还使用真正的 Cockpit 9090 端口、PHP/MySQL 站点及自定义 SUID 程序 `Authchecker`；目前没有核实到原版 Blaze 网站/自定义 ELF 的可授权源码，因此不应将自编站点冒充原题。

本项目优先研究并实现 *PG Pebbles* 这台具有**公开原始 Web 应用源码**的 SQLi 靶机。若最终不能在平台的 Docker 隔离边界内完整、安全地复现 UDF Root 链，要明确记录差异与不支持原因，不交付假提权链。

## 7. 第二轮核查：原始软件包比自行重写更容易

- 初始 TCP 80 的 Pebbles PHP 登录页面是**非主要利用入口**。不同 Writeup 均指出常见账号/SQLi 测试不成功；不能将这里伪造为真正 SQLi。已在 `site80/` 复原行为，原版网页静态素材尚未找到，所以未承诺像素级还原。
- 上游 ZoneMinder 2016 年文档明确指出 Ubuntu 16.04 官方仓库包含 **ZoneMinder 1.29.0**，依赖 PHP 7.0 + MySQL 5.7 + Apache，可先使用历史 Ubuntu 系统包而非为原版应用自行写 HTML/CSS。
- 真实漏洞的 **CVE 是 CVE-2016-10204**：日志查询中的 `limit` SQL 注入。CVE-2016-10203 是另一个 XSS，不能混淆。
- `probe/Dockerfile.package-probe` 仅安装历史包并检查版本及文件是否存在；文件名故意**不是 Dockerfile**，以防未经验证的原型被现有 GHCR 自动构建工作流当成靶机发布。
- 虽然当前工作区没有本地 Docker 引擎，**GitHub Actions 已经用实际 Docker 完成旧版包、真实 SQLi 与 UDF 运行验证**。这些结果仍不代替真实 Worker 部署与宿主隔离验收。

**上游依据：** https://wiki.zoneminder.com/Ubuntu_Server_16.04_64-bit_with_Zoneminder_1.29.0_the_easy_way ；漏洞说明：https://ubuntu.com/security/CVE-2016-10204

**研究分支：** https://github.com/10010100111000/AttackBoxModule/tree/feat/pebbles-original-entry/labs/pebbles/
