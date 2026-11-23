# trytopwn Web 题库覆盖现状与滚动路线图（v2）

更新：2026-11-23。**选题依据是 PortSwigger 式的细分知识点和不同真实利用场景，不是“每种漏洞三台”“做满九台就停止”。**

先看：[31 专题 / 219 知识目标](../catalog/web-competencies.json) → [分类与难度](WEB_TAXONOMY.md) → [候选机器与评分方法](WEB_MACHINE_SELECTION.md) → [机器及滚动队列](../catalog/web-curriculum.json)。

## 一、当前存量：17 个目录（Web 16 + 非 Web 服务链 1）

**以下是仓库快照与原有 CI 证据**；“有完整目标链 CI”不代表每个相关知识目标都有单独的专项断言，也不代表已在真实 Worker 上线。

| 靶机 | 暂定级别 | 主要训练类别 | 典型场景差异 | 验收状态 |
| --- | --- | --- | --- | --- |
| base | 初级 | 认证与会话安全 | 原生文件上传 | 尚无完整验收 |
| bashed | 初级 | 暴露的管理或执行接口 | Web shell | 完整目标链 CI（非 Worker） |
| bike | 初级 | 模板注入 | 模板上下文 | 局部/目标未全验收 |
| bountyhunter | 中级 | XML 外部实体 | 真实外部实体 | 完整目标链 CI（非 Worker） |
| cap | 中级 | 对象级授权与 IDOR | 越权获取其他人的网络流量 | 完整目标链 CI（非 Worker） |
| cursed-stale-policy | 高级 | 跨站脚本 | 管理员浏览器 / CSP | 尚无完整验收 |
| devvortex | 中级 | CMS / 应用组件漏洞 | CVE 信息泄露 | 局部/目标未全验收 |
| editorial | 中级 | 服务端请求伪造 | 服务端 HTTP 请求到回环 API | 完整目标链 CI（非 Worker） |
| goodgames | 中级 | SQL 注入 | SQLi 与存储模板上下文 | 局部/目标未全验收 |
| nibbles | 初级 | 文件上传 | 真实原版上传文件处理 | 完整目标链 CI（非 Worker） |
| openadmin | 中级 | 命令注入与系统调用 | 旧版本原生命令执行 | 完整目标链 CI（非 Worker） |
| pebbles | 高级 | SQL 注入 | 真实数据库文件操作 | 完整目标链 CI（非 Worker） |
| photobomb | 中级 | 命令注入与系统调用 | 真实命令拼接及执行 | 完整目标链 CI（非 Worker） |
| shocker | 初级 | 命令注入与系统调用 | 旧 Bash 环境函数解析 | 完整目标链 CI（非 Worker） |
| union | 中级 | SQL 注入 | UNION/LOAD_FILE与请求头 shell | 完整目标链 CI（非 Worker） |
| validation | 中级 | SQL 注入 | 真实二阶 SQLi | 完整目标链 CI（非 Worker） |
| funnel | 初级 | 非 Web 服务链与协议枢纽 | 非 Web 网络服务 | 局部/目标未全验收 |

目前旧清单有 **11 项 full_chain_ci、4 项 partial、2 项 unverified**（按历史标记，不是 31 专题的覆盖率）。Worker 正式发布仍须独立验收；Editorial 有 .release-blocked 标记，代码虽已合并但不能据此发布。

## 二、每个知识点的“覆盖”要怎么计算

以 [catalog/web-competencies.json](../catalog/web-competencies.json) 的 219 个目标为索引，每个目标关联 0..N 条场景变体、每个变体关联 0..N 台真实靶机。

长期维护 3 个不同指标：

1. **知识点覆盖**：多少个 skill_id 存在针对其机制的实际成功验收证据？不是只要在 README 提过就算。
2. **场景深度**：同一 skill_id 在多少个**实质不同**的输入面、反馈模式、数据库/框架、校验约束、浏览器/协议边界下训练过？同点重复**可以加分**。
3. **梯度完整性**：该技能在初级、中级和高级场景是否分别有适宜学习任务？不要求每项强行做三台，但核心知识点要有向上递进路径。

**最重要的规则：不限机器数量。** 即使当前 SQLi 已有四台，只要新机器能训练真实布尔盲注、时间盲注、XML 编码绕过、WebSocket、PostgreSQL 方言等新变体，都可以继续选择。

## 三、SQLi：具体在哪些方向重复才有价值？

| 知识方向 | 已有关联（不代表子项专项验收） | 新场景建议 |
| --- | --- | --- |
| 认证逻辑与基本查询 | GoodGames（仅部分验收） | 登录之外的查询过滤、JSON 结构、Cookie |
| UNION 输出 | Union、Validation | 列数探测与数据类型、PostgreSQL/SQLite 差异、受限制输出 |
| 二阶 SQLi | Validation | 与登录/预约/订单等后续消费点组合 |
| DB 文件操作 | Pebbles、Union、Validation | 文件权限受限、数据库与文件系统不同用户 |
| **布尔盲注** | 暂无该机制专门验收 | Cookie/隐藏 API、不同真/假响应，真实数据提取 |
| **时间盲注** | 暂无该机制专门验收 | 多轮延时统计、PostgreSQL/MySQL 方言差异 |
| **报错型/条件报错** | 暂无该机制专门验收 | 常规报错与条件错误分别对照 |
| **OAST/过滤绕过** | 暂无该机制专门验收 | 独立内网回调、XML 编码、WAF/解析器差异 |
| **WebSocket 盲注** | 暂无该机制专门验收 | Soccer 候选：实际 WS 服务传输和权限边界 |

**不能**因 Union 已有 UNION 就取消未来其他 UNION 题。如果数据库类型、列输出限制、输入面或真正的防护约束不同，仍可保留。不要把不同难度建立在换个前端颜色上。

## 四、XSS：目前核心短板，按浏览器上下文建立递进

| 子能力 | 当前现状 | 建议增加的不同场景 |
| --- | --- | --- |
| 反射型 / HTML 正文 | 无可信专属验收 | 查询/搜索结果页 → 真浏览器执行 |
| HTML 属性与 JavaScript 字符串 | 无 | 参数引用、属性转义、JS 模板上下文 |
| 存储型 | 无可信专属验收 | 评论/工单/管理员查看页、不同权限受害者 |
| DOM-based | 无 | hash、postMessage、localStorage 与危险 DOM sink |
| Blind XSS | 无 | Headless 候选：支持表单 User-Agent、管理员会话 |
| CSP 绕过 | Cursed Stale Policy 有代码，但**未验收完整链** | 先核实现有题，再考虑其他 CSP 配置的重复题 |
| 浏览器执行到权限影响 | 无 | 真浏览器完成管理员权限操作；不只出现 alert() 文字 |

真实浏览器管理员 Bot 对隔离、CPU/RAM 要求更高，不能用服务器返回一段 HTML 就算通过。

## 五、其余 29 个专题都必须进入计划，而不只是 SQLi/XSS

其它技能也已经完整编目，以下列出当前选题方向（详细子目标见 JSON）：

| 方向组 | 候选训练技术 |
| --- | --- |
| 服务端核心 | Authentication、Path traversal/LFI、Command injection、Business logic、Information disclosure、Access control、File upload、Race conditions、SSRF、XXE、NoSQL injection、API testing、Cache deception |
| 客户端 | CSRF、CORS、Clickjacking、DOM-based、WebSockets |
| 进阶 | Deserialization、Web LLM、GraphQL、SSTI、Cache poisoning、Host header、Request smuggling、OAuth、JWT、Prototype pollution、Essential skills |

其中初级题并非必然来自官方 Server-side 组。JWT、GraphQL 或 Prototype pollution 也需要基本概念题，而高级 SSRF/SQLi 需要更强限制和复杂反馈。**题目类型、难度、知识点是三个独立维度**。

## 六、持续滚动的下一批选题：不设固定九台上限

当前 [web-curriculum.json](../catalog/web-curriculum.json) 记录 **33 条待开展的技能/场景需求**；这不是 33 台机器的开发承诺，也不是所有需要覆盖的 219 个技能的终点。

| 滚动优先组 | 预期知识目标 | 实物候选或来源约束 |
| --- | --- | --- |
| **基础概念与浏览器** | 反射 XSS 的 HTML/属性上下文、基础路径遍历、NoSQL 操作符查询 | 首先寻找有公开源代码或原版可观察行为的真实应用，不能造假的漏洞接口 |
| **SQLi 递进** | 条件响应、报错、时间盲注、带外与不同数据库方言 | 可重复选 SQLi 综合靶机；Soccer 的 WebSocket 盲注与 Union 的 UNION 不是重复训练 |
| **浏览器/会话进阶** | 存储/DOM/Blind XSS、CSP、CSRF、JWT、OAuth | Headless 是 Blind XSS 候选；Cursed 需先独立验证 |
| **实际应用组件** | NoSQL + 反序列化、LFI + 真 CVE、Ruby PDF 转换 | NodeBlog、Trick、Inject、Precious，必须逐一核实原版软件版本 |
| **协议与高复杂度** | WebSocket、Race、API/GraphQL、Request Smuggling、Cache、Prototype pollution、LLM | 要有真实解析器、代理、数据库、浏览器/代理环境与独立测试 |

### 现已找到正式页面的机器候选（尚未批准开发）

| HTB 机器 | 公开资料支持的典型链 | 规划中的增量价值 |
| --- | --- | --- |
| [Headless](https://www.hackthebox.com/machines/headless) | Python Werkzeug、Blind XSS 经管理员浏览器 | User-Agent + 管理员 Bot，补 XSS 较深场景 |
| [Trick](https://www.hackthebox.com/machines/trick) | DNS/vhost、SQLi 文件读、LFI | 多站点真实发现，路径遍历/LFI/SQLi 不同组合 |
| [NodeBlog](https://www.hackthebox.com/machines/nodeblog) | Node/Express、NoSQL、反序列化线索 | 真实 MongoDB/序列化栈，与 SQLi 区分 |
| [Precious](https://www.hackthebox.com/machines/precious) | Ruby/PDFKit、YAML 处理 | 引入不同语言的反序列化与依赖漏洞 |
| [Soccer](https://www.hackthebox.com/machines/Soccer) | Tiny File Manager、WebSocket SQL 盲注 | WS 数据通道、盲注反馈、多阶段 Linux 提权 |
| [Inject](https://www.hackthebox.com/machines/inject) | 上传中的 LFI → Spring Cloud Function | Java 栈 LFI 与真实 CVE，区别于 PHP |

更完整的十台候选与量化评审标准请看 [WEB_MACHINE_SELECTION.md](WEB_MACHINE_SELECTION.md)。正式开发时仍须查证 Writeup/源码，确定版本，并且不能声称未公开的原题源码可得。

## 七、如何选择与提交下一台

1. **先选知识目标**：web-competencies.json 里的一个或多个 skill_id，并给出初/中/高级的场景深度。
2. **允许重复，但需有学习增量**：明确输入面/反馈/约束/技术栈/侦察/目标至少一项实质变化；记录 variant_id。
3. **再找原版资料**：HTB/OffSec 题、历史 Writeup、漏洞公告和上游项目；优先真实存在的原版易受影响组件。
4. **按选题规则评分**：来源真实性、知识差异、侦察自然性、CI 可复现性、Docker 约束、镜像资源；原则上不少于 75/100，硬性不合规则不准开发。
5. **单机单 PR**：独立攻击容器从外部服务验证真实利用、目标 Flag、原生 Root 或其它目标、健康检查、实例隔离/重置和实测镜像字节数。
6. **区分发布**：源码进入 main 和实验室 CI 通过，都不是 Worker 发布许可；未验证的场景保持未验证。
7. **持续更新知识点**：成功后在目标技能下新增已验证的 variant_id 与 CI 证据。旧靶机可以补细分专项测试，不必每个目标都造新靶机。

## 八、下次续作约定

下次用户说“继续制作靶机”，先读取本文件、[分类](WEB_TAXONOMY.md)、[选题](WEB_MACHINE_SELECTION.md) 与两个 catalog/*.json，再比较 main、已合并 PR 与新 CI，选择适合的真实案例。

**最关键的变化：题库既要横向全覆盖 Web 安全技术，又要纵向让同一个知识点从入门到复杂场景反复出现。选题服务于知识点，而不是知识点迁就手头的靶机。**
