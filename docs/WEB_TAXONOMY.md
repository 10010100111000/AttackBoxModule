# trytopwn Web 题库分类与难度标准（v1）

更新：2026-11-23。此文档和 [结构化清单](../catalog/web-curriculum.json) 共同作为后续选题约束。参考 OWASP Web Security Testing Guide / PortSwigger Web Security Academy 的知识结构；具体实战靶机以可核实的 Writeup、原始组件与代码为依据。

## 1. 两个正交维度：题型 × 难度

- **主漏洞类别（`primary_category`）**：每台靶机必须且只归属一个类别，用来统计题库覆盖。选择玩家主要需要学习、发现和利用的首要 Web 技术，不按“最后拿到 Root 的方法”机械分类。
- **次要类别与细分技能（`secondary_categories`、`implemented_skills`）**：记录真实攻击链中的其他知识点，例如 SQLi → 凭据 → SSH → sudo。不用它们给主类别重复计数。
- **难度（`provisional_difficulty`）**：初级／中级／高级；现有映射是**暂定评估**，以后结合真实玩家成功率、所需背景和发现成本调整。不能直接照搬 HTB 难度，也不能凭 CVE 数量决定。
- **题目形式（`track`）**：`web` 是以 Web 为主的靶机，`service` 是非 Web 服务链。开发时另区分**Web 专项**（一个知识点，可单 Flag）与**Web 综合靶机**（真实侦察、Foothold、横向移动／系统提权，通常 User + Root 两阶段）。一个专项也可以高级，一个综合靶机也可以初级。

### 三级难度定义

| 级别 | 学习与发现要求 | 典型验收重点 |
| --- | --- | --- |
| **初级** | 认识单一漏洞原理、基本请求修改、可理解的反馈；允许简单枚举，不能开页即明示漏洞位置 | 真实漏洞请求、预期权限边界、无明显绕题捷径 |
| **中级** | 无直接回显、多个页面／服务、角色关系、凭据复用或真实本地提权；需要独立分析上下文 | 从外部入口完整复现、实际用户切换、逐环节取证 |
| **高级** | 边界与过滤限制、盲利用、多协议／多组件、CSP/浏览器约束、逻辑或竞争窗口；较长侦察路径 | 限制条件真正生效、可重复独立验收、可测的资源成本 |

高级不等于“必有 Linux Root”，初级也不等于“只允许一个页面”。难度可在评估后调整，但**技能标签不能为凑数而虚报**。

## 2. 规范化漏洞大类

| ID | 漏洞类别 | 需要循序覆盖的技能 |
| --- | --- | --- |
| `auth_session` | 认证／会话／CSRF／JWT | 登录绕过 → 权限与会话管理 → JWT/CSRF 与跨功能链 |
| `sqli` | SQL 注入 | 登录绕过／UNION → 报错／布尔／时间盲注 → 二阶／文件操作／带外与绕过 |
| `xss` | XSS | 反射型、存储型 → DOM、管理员浏览器 → Blind XSS、CSP 绕过 |
| `ssrf` | SSRF | 本地／内网请求 → 跳转与 URL 校验 → Blind SSRF 与内部服务链 |
| `idor` | IDOR 与对象授权 | 对象 ID 越权 → 多角色 → 多租户授权边界 |
| `file_upload` | 文件上传 | 无限制上传 → 文件校验绕过 → 解析差异／竞态 |
| `file_read` | 路径遍历／LFI | 读取路径 → 配置／会话文件 → 包装器与 LFI 组合 |
| `command_injection` | 命令注入／Shellshock | 基础命令执行 → 参数／环境注入 → 盲执行和过滤 |
| `ssti` | SSTI | 模板表达式 → 对象与模板上下文 → 沙箱约束 |
| `xxe` | XXE | 本地文件 → 内网 SSRF → Blind/OOB |
| `nosql` | NoSQL 注入 | 操作符认证绕过 → 盲提取 → 复杂逻辑 |
| `deserialization` | 不安全反序列化 | 不安全解析 → 真实库的 Gadget 链 → 复杂约束 |
| `business_logic` | 业务逻辑漏洞 | 流程／金额／状态检查 → 多步骤状态机 |
| `race_conditions` | 竞态条件 | TOCTOU → 并发请求和多步骤竞态 |
| `http_protocol` | HTTP 协议与边界 | Host / WebSocket → Request Smuggling／Cache 攻击 |
| `cms_vulnerability` | CMS／依赖组件 | 版本识别／信息泄露 → 插件／已知 CVE |
| `exposed_interface` | 暴露的执行或管理入口 | 未发现的 Web Shell、管理控制台 |
| `service_pivot` | 其他服务链（单列非 Web） | FTP → SSH Tunnel → DB 访问 |

以上类别用于归档与选题；同一靶机可有多个不同阶段，但**主类别唯一**。

## 3. 统一验收状态：绝不混用

1. `unverified`：文件存在，尚未有独立完整目标攻击链证据。
2. `partial`：基本服务、局部漏洞或单 Flag 已验证，但不足以声称完整目标链。
3. `full_chain_ci`：独立攻击容器／真实环境通过预定目标链，且可追溯到 CI 运行或验收脚本；只代表**靶机 CI**。
4. `worker_status = not_verified`：即使 `full_chain_ci` 通过，也还不能声称生产平台可上线；还需专用私网、隔离、Flag 判题与重置、容量和并发验收。
5. `release_status = blocked_by_marker`：存在 `.release-blocked`，发布器会拒绝该靶机。其它靶机的 `not_assessed` **不代表允许发布**。

“完整目标链”按题型设计：Web 专项可以一枚 Flag；Web 综合靶机若声明 User/Root，则必须逐一验证。真实 SSH／sudo／服务组件不可由假的成功消息代替。

## 4. 以后每个靶机 PR 必须给出的信息

- **出处**：历史 Writeup、上游项目链接、固定版本、漏洞编号（适用时）、原版源码／行为复现区别及许可证。
- **标签**：唯一主类别、细分技能、建议难度、题目形式、预期所需技能。
- **发现路线**：扫描 → 枚举 → 线索 → 漏洞验证 → 目标 Flag；不要把参数和漏洞直接写在首页告诉玩家。
- **实现**：真实易受影响组件与利用路径、Dockerfile、服务配置、最小镜像、健康检查、限额、无公网漏洞端口、无容器逃逸。
- **验收**：独立攻击端从外部服务拿到每个目标 Flag；用户/Root 权限检查；每次重置旧 Flag 失效与环境清空；CI 公开结果，报告实际镜像大小。
- **上线前**：Worker 实测私有网络和跨用户隔离、容器能力／sudo 与安全参数相容、服务器端 Flag 验证、并发资源占用。

**不允许**：模拟 SQL 引擎、伪造漏洞响应、测试时直接把 root.txt 打印成攻击成功、把未验证 Root 的靶机写成“全链通过”。

## 5. 维护规则

每合并一台靶机：
1. 在 `catalog/web-curriculum.json` 新增机器记录并更新证据、状态和技能；不改变旧主分类来“美化覆盖率”。
2. 在 [路线图](WEB_ROADMAP.md) 更新表格／已完成项，并将对应 `backlog` 的状态从 `planned` 改为 `in_progress` 或 `done`；有新缺口再补计划。
3. 如果完整攻击链测试失败，标注 `partial` 或 `unverified`，不能以镜像构建通过取代。
4. 任何 `.release-blocked` 的删除必须有独立的 Worker 审核依据，不得只因 GitHub CI 绿灯删除。
