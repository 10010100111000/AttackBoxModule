# main 分支现有靶机清单

**快照日期：2026-11-27**  
**基准提交：** `bb3d62f3f8f96ded4eb34b16ba2561a4a1e0f678`  
**范围：** 只盘点 `main` 已有的 Lab 代码、Challenge 内容、CI 证据与尚未完成的靶机本身。不管理 Worker、平台同步或生产发布流程。

## 总览

当前目录清单有 **27 台 Lab**：

| main 中记录的 CI 状态 | 数量 | 含义 |
|---|---:|---|
| `full_chain_ci` | 19 | 保留了历史完整目标链 CI 证据；不代表当前 CI 会继续自动执行攻击链 |
| `partial` | 4 | 已有部分真实功能或目标行为检查，仍有靶机内容/目标路径缺口 |
| `unverified` | 4 | 尚无足够的靶机目标验证记录 |

另有 **11 台**保留 `.release-blocked` 标记。该标记不是 CI 结果，也不等同于靶机代码不存在；未完成原因应以各自 README 和标记文件为准。

### 最近更新：Bike

Bike 已在 main 合并，代码提交为 `05f5c1048a297961e0ff42745e8fae2fbc39bfe2`。使用受影响的 Handlebars 4.1.1，独立 HTTP 攻击端从 Web 入口完成 SSTI 命令执行并读取随机 Flag。

- [PR 独立攻击端 E2E](https://github.com/10010100111000/AttackBoxModule/actions/runs/45899322346)：包含题目验证器和 Writeup 独立利用脚本
- [main 版本化 Flag 发布 E2E](https://github.com/10010100111000/AttackBoxModule/actions/runs/45899503806)：生成 0.1.0 随机 Flag，实际读取并验证后提交发布文件
- [main 题库目录一致性 CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/45899891027)：通过
- 镜像大小约 **80.8 MB**；测试时容器内存约 **18.4 MiB**（700 MiB 限额）

Flag seed、版本 Manifest 与 Challenge 答案已由 CI 核对一致。Bike 是 Web-only 单 Flag，不包含 SSH 登录或第二阶段 Root 提权。

### Precious 完整 E2E 验收

Precious 已完成独立攻击端端到端验收。真实 PDFKit 0.8.6 / wkhtmltopdf 靶机在隔离 Docker 网络中，通过 CVE-2022-25765 以 `ruby` 身份执行命令，并读取本次 CI 生成的精确随机 Web Flag。

- [独立攻击端 E2E](https://github.com/10010100111000/AttackBoxModule/actions/runs/45901870712)：命令执行身份与 Web Flag 回读均通过
- [普通 PDF 功能 smoke CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/45901579321)：首页、PDFKit 版本、健康检查和正常 PDF 转换通过
- [镜像构建与启动检查](https://github.com/10010100111000/AttackBoxModule/actions/runs/45901579285)：通过
- Docker 镜像约 **190.9 MB**；测试时内存约 **21 MiB**（850 MiB 限额）

Flag 由每次 CI 独立生成，并核对目标文件与 Challenge 答案一致。题目仍为 Web-only 单 Flag，不包含 SSH、YAML 反序列化或 Linux Root 阶段。

## CI machine index

This table is generated from the same state recorded in `catalog/web-curriculum.json`. The curriculum CI compares every row, count and release marker; update this table whenever the catalog changes.

| Lab ID | Catalog CI status | Release marker status |
|---|---|---|
| `alert` | `partial` | `blocked_by_marker` |
| `base` | `unverified` | `not_assessed` |
| `bashed` | `full_chain_ci` | `not_assessed` |
| `bike` | `full_chain_ci` | `not_assessed` |
| `bountyhunter` | `full_chain_ci` | `not_assessed` |
| `cap` | `full_chain_ci` | `not_assessed` |
| `cursed-stale-policy` | `unverified` | `not_assessed` |
| `devvortex` | `partial` | `not_assessed` |
| `editorial` | `full_chain_ci` | `blocked_by_marker` |
| `goodgames` | `partial` | `not_assessed` |
| `nibbles` | `full_chain_ci` | `not_assessed` |
| `openadmin` | `full_chain_ci` | `not_assessed` |
| `pebbles` | `full_chain_ci` | `not_assessed` |
| `photobomb` | `full_chain_ci` | `not_assessed` |
| `precious` | `full_chain_ci` | `not_assessed` |
| `shocker` | `full_chain_ci` | `not_assessed` |
| `union` | `full_chain_ci` | `not_assessed` |
| `validation` | `full_chain_ci` | `not_assessed` |
| `funnel` | `partial` | `not_assessed` |
| `django-debug-xss` | `full_chain_ci` | `blocked_by_marker` |
| `wondercms-xss` | `full_chain_ci` | `blocked_by_marker` |
| `usage` | `full_chain_ci` | `blocked_by_marker` |
| `nodeblog` | `full_chain_ci` | `blocked_by_marker` |
| `zipping` | `full_chain_ci` | `blocked_by_marker` |
| `soccer` | `full_chain_ci` | `blocked_by_marker` |
| `trick` | `unverified` | `blocked_by_marker` |
| `intense` | `unverified` | `blocked_by_marker` |

## 现有靶机状态

### 已有完整目标链 CI 记录（19 台）

| Lab | 主要技术/目标 | 备注 |
|---|---|---|
| Bashed | phpbash 暴露入口、sudo/cron | 原版 phpbash 组件 |
| Bike | Handlebars 4.1.1 SSTI → RCE | 独立 HTTP 攻击端读取随机 Flag；PR 与 main 版本发布 E2E 均通过 |
| Bountyhunter | SimpleXML XXE、凭据与后续服务链 | 真实 XML 解析器 |
| Cap | IDOR、PCAP、凭据复用、Linux capability | 已拆分为 Packet Drop / Setuid Surprise 两个 Challenge |
| Django Debug XSS | Django 1.11.4 技术错误页 XSS | 有真实浏览器与版本负向对照记录；有 `.release-blocked` |
| Nibbles | Nibbleblog 插件上传 | 真实 Nibbleblog 4.0.3 |
| OpenAdmin | OpenNetAdmin xajax RCE | 真实 ONA 18.1.1 |
| Pebbles | ZoneMinder SQLi、数据库文件操作 | 历史依赖栈较复杂 |
| Photobomb | ImageMagick 命令注入 | Sinatra / ImageMagick |
| Shocker | Bash CGI Shellshock | 真实 GNU Bash 4.3 |
| Union | MariaDB UNION / LOAD_FILE | 后续链涉及网络权限边界 |
| Validation | 二阶 SQLi、MariaDB FILE | 真实 MariaDB 与 PHP |
| Editorial | SSRF、内部 API、GitPython | 有 `.release-blocked` |
| Usage | Laravel password recovery SQLi | 有 `.release-blocked` |
| NodeBlog | MongoDB NoSQLi、XXE、node-serialize | Web-only，多阶段 Challenge；有 `.release-blocked` |
| Zipping | ZIP symlink、SQLi/FILE、PHP LFI | 使用的解压组件与原题存在差异；有 `.release-blocked` |
| Soccer | Tiny File Manager、WebSocket blind SQLi | Web-only；有 `.release-blocked` |
| WonderCMS XSS | WonderCMS 属性上下文 XSS、管理员浏览器 | 有 `.release-blocked` |

`full_chain_ci` 表示该 Lab 有完整目标链 CI 证据；旧 Lab 的历史证据不自动等同于当前统一 E2E 标准。每台是否通过新标准，以 `catalog/web-curriculum.json` 中的 `e2e_ci_status`、运行链接和提交 SHA 为准。Bike 与 Precious 均已按新标准通过独立攻击端验收。

### 部分完成（4 台）

| Lab | 已有内容 | 仍需处理的靶机工作 |
|---|---|---|
| Alert | Markdown 存储型 XSS、真实 Chromium 管理员浏览器、内部文件读取 | Web Flag 目标路径仍需人工确认；有 `.release-blocked` |
| Devvortex | Joomla 4.2.6 信息泄露 | 明确并完成 Web 专项目标；不要默认追加 Linux Root |
| GoodGames | 登录 SQLi、凭据线索、存储型 Jinja2 SSTI | 整理单 Web Flag 目标与完整 Challenge/Writeup |
| Funnel | FTP、SSH、PostgreSQL 隧道 | 属于非 Web 服务链，单独标识其题库归类与目标 |

### 尚未充分验证（4 台）

| Lab | 当前实现 | 下一步关注 |
|---|---|---|
| Base | PHP 7.2 strcmp 认证逻辑、文件上传 | 明确真实请求处理和 Flag 目标 |
| Cursed Stale Policy | CSP、XSS、WebSocket 相关代码 | 先核对实际浏览器行为，不把代码存在当成漏洞已成立 |
| Trick | DNS、PHP、MariaDB、LFI、Fail2ban 等真实服务 | 当前实现较复杂，先整理正常业务与题目范围，再补基础工程检查 |
| Intense | Flask、SQLite 条件错误、LWT 会话、路径遍历 | Web-only 初始实现；先完成构建、启动与普通功能 |

## 接下来只处理 main 已有靶机

建议顺序：

1. **GoodGames**：整理 SQLi → Jinja2 SSTI 的自然探索路径与单 Flag 目标。
2. **Devvortex**：明确 Web-only 目标，不把原题 Linux 后半段强加进来。
3. **Base**：补清楚认证与上传两部分的实际功能和题目目标。
4. **Intense / Trick**：先处理复杂实现的基础工程与文档，不扩展新功能。

这只是 main 现有资产的处理顺序，不代表上述靶机已经全部通过人工漏洞验收。完成一台后，再按实际差异更新本清单和 `catalog/web-curriculum.json`。

## 维护规则

- `catalog/web-curriculum.json` 是 Lab 状态、候选与 backlog 的结构化主清单。
- `catalog/web-competencies.json` 是技能分类和验收目标的唯一来源。
- `labs/<slug>/README.md` 记录该 Lab 的真实组件版本、部署、功能和已知差异。
- `challenges/` 存放玩家题面；适合的题目附带 `writeup.md`。
- CI 只检查构建、启动、healthcheck 和普通功能，不添加自动攻击链、自动 Flag 提取或模拟漏洞。
- 不因为 CI 普通功能通过就把漏洞利用路径标记为已人工验收。
- 暂停新增 Lab；优先完成以上 main 已有靶机。
