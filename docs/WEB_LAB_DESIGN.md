# trytopwn — Web 靶机全套设计与开发计划

> **唯一内容规划入口** · v3 · 2026-11-27
>
> 面向 PortSwigger Web Security Academy 风格的 **Web 技术分类、细分技能、难度递进、真实靶机选择、当前覆盖缺口、下一台决策与完整验收**。这不是仅描述 Docker 或 Worker 的工程规范。保留原有 31 专题、219 技能和全部历史候选，不推倒重做。
>
> **长期数据真值**：[31 专题/219 技能能力矩阵](../catalog/web-competencies.json) · [机器状态/候选/滚动 backlog](../catalog/web-curriculum.json)。逐台执行、E2E、合并和新会话交接流程见 [Lab Production Playbook](LAB_PRODUCTION_PLAYBOOK.md)。当前 main 机器状态以结构化清单为准。

## 验证职责调整（2026-11-27，当前规则）

用户明确要求：**不要再要求用户逐台手动验证。每台靶机的预期题目流程应由 GitHub Actions 自动走完并验证最终 Flag。**

每台 Lab 的 CI 分为两层：

1. **工程检查**：Docker 构建、容器启动、healthcheck、正常页面/业务功能、资源限制和目录/配置一致性。
2. **题目端到端验收**：使用独立攻击端（单独容器或进程），只通过靶机正常暴露的网络接口，按题面预期的侦察与利用路径操作真实易受攻击组件，最后读取本次实例实际生成的 Flag，并核对其与 Challenge 答案一致。

端到端测试必须满足：

- 使用真实受影响版本、真实组件和实际业务入口，不允许模拟漏洞接口、伪造命令执行或测试后门。
- 攻击端不得挂载靶机文件系统、共享 Docker socket、使用 `docker exec` 读取 Flag，或绕过题目流程直接查询目标内部数据。
- 目标与攻击端使用隔离的临时网络；不把故意脆弱的靶机暴露到公网。
- 按每台题目的真实目标验收；Web-only 题目只验证 Web Flag，不强制 SSH、sudo、Root 或双 Flag。
- 动态 Flag 应由 CI 按版本生成；同一版本保持稳定，新版本按发布规则轮换。
- 关键步骤失败、无法取回正确 Flag、Flag 不一致或服务异常，端到端 CI 必须失败。
- 历史完整链 CI 仅作为历史证据；只有按当前规则实际运行成功的专属工作流，才能把 `e2e_ci_status` 更新为 `passed`。

| 层次 | 负责内容 | 通过时能说明什么 |
| --- | --- | --- |
| 工程 CI | 构建、启动、healthcheck、普通功能、资源与结构检查 | 镜像可构建、服务可启动 |
| Lab 端到端 CI | 独立网络攻击端完成真实题目路径并取得精确 Flag | 该提交版本的预期题目流程在隔离 CI 环境可完成 |
| 结果记录 | 在 `catalog/web-curriculum.json` 记录工作流、状态、提交 SHA 和运行链接 | 哪些 Lab 已接入、通过、失败或仍待接入 |
| 平台发布 | Worker 私网/资源隔离、生命周期、Web 判题与答案失效 | 是否可在正式平台发布；不由本地 Lab CI 代替 |

状态字段：`pending`（未接入）、`configured`（已有专属工作流，尚未按当前版本确认通过）、`passed`（当前工作流端到端成功）、`failed`（最近验收失败并记录原因）。不得因普通 smoke 成功而标记端到端通过。

## 当前验收状态核对（2026-11-27）

以 main 提交 `bb3d62f3f8f96ded4eb34b16ba2561a4a1e0f678` 为本次盘点基准：

- 当前目录有 **27 台 Lab**：22 台记录为 `full_chain_ci`、2 台为 `partial`、3 台为 `unverified`。
- 端到端 CI：**Bike、Precious、GoodGames、Devvortex 与 Base 5 台 passed、22 台 pending**；Devvortex 的 0.1.0 版本化 Flag 也已通过真实攻击链发布验收。
- 其中 **10 台**保留 `.release-blocked` 标记；该字段与 CI 结果分开记录。
- 技能目录仍为 **31 个专题 / 219 个细分目标**。
- 滚动队列为 **35 项**：4 项 done、4 项 in_progress、27 项 planned。
- Precious 已通过专属普通功能 CI、镜像构建和独立攻击端 E2E。端到端测试通过真实 PDFKit 0.8.6 命令注入，以 `ruby` 身份读取本次随机 Web Flag；不包含 SSH、YAML 反序列化或 Root 阶段。

本次清单与执行顺序见 [现有 main 靶机清单](EXISTING_WEB_LAB_RELEASE_INVENTORY.md)。不要再使用 2026-11-25 之前的机器数量、CI 分类或候选顺序作为当前状态。

## 如何用这份文档选择下一台靶机

**2026-11-25 Web 专项规则（用户确认）**：默认任务是 Web 目标攻击链的完成，不要求 SSH、sudo、Linux root 或双 Flag。典型闭环包括认证绕过、文件读取、脚本执行、Web 端 RCE、受害者浏览器动作或读取指定 Web 目标。只在用户明确要求“完整靶机”时复现独立的 Linux 提权链；不要因原题后半段涉及 Linux 而误判 Web 专项为未完成。Flag 的数量和位置服从实际 Web 目标。题库候选同时覆盖 HTB、OffSec/PG 与公开可信的其他真实靶机，以知识点难度从基础到高阶推进；不为凑数量发明漏洞或强制 root。


1. 在 **技术分类与训练梯度** 找一个明确的 `skill_id`，不是只说“再做一台 SQLi”。
2. 在 **滚动开发路线与知识缺口** 查已有机器、人工验收记录、历史 CI 证据、难度和缺口；*已有完整链 CI ≠ 该机器涉及的全部技能均已独立验收*。
3. 在 **选题评审与真实靶机候选** 比较原版技术/公开 Writeup、输入面、数据库或浏览器行为、镜像资源。不得用假接口或冒充真实 CVE。
4. 把决定与后续证据写回 `catalog/web-curriculum.json`，选题的唯一主/次 `skill_id` 均来自 `catalog/web-competencies.json`。同技能可以重复，但必须说明增量。
5. 完成真实 Docker、启动/健康检查与基础 CI。题目完整流程与 Flag 由专属端到端 CI 自动验收并记录；没有实际运行证据不能汇报为验收通过。Worker 实机、Web 判题对接与正式发布另行验收。

**后续开发优先逻辑**：先补有意义的知识缺口 → 对照已实现机器 → 验证真实候选与原始版本 → 制作/CI → 更新覆盖数据 → 再选下一台。禁止按固定靶机数量配额规划课程。

## 文档职责

| 入口 | 唯一职责 |
| --- | --- |
| **本文件** | Web 分类、教学/训练梯度、历史候选与选择规则、覆盖及选题优先级、交付边界 |
| `catalog/web-competencies.json` | 31 类/219 个细分技能的结构化权威列表，包含每个 skill 的验收要求 |
| `catalog/web-curriculum.json` | 当前机器、候选与 backlog、CI/Worker 状态（实时记录） |
| `labs/<slug>/README.md` | 该靶机真实源码/配置、利用路径、Docker、镜像、测试与风险证据 |
| `challenges/<category>/<slug>/<title>.md` | 平台实际给学员的题面（不暴露答案） |
| `.github/workflows/` | CI 与发布门禁；不通过不能声称靶机完成 |

## 技术分类与训练梯度


**更新：2026-11-23。以 PortSwigger Web Security Academy 的公开专题结构为参考，但知识点、变体场景及难度规则均为 trytopwn 独立编写；不复制官方练习。**

#### 一、为什么不能用“每类至少三台”规划题库

以前的规划很容易变成 SQLi 三台、XSS 三台，完成数量后便停止。同一类别内部包含彼此完全不同的攻击机制；即使相同机制，也可能在输入面、回显方式、限制条件和数据库语法上存在值得反复训练的变体。

**新的基础结构：`专题（topic） → 细分知识点（skill） → 场景变体（variant） → 真实靶机（lab） → 独立验收证据（evidence）`。**

- **专题数不等于覆盖率**：某台机器含 SQLi，只说明它涉及 SQLi，不代表盲注、报错、OAST 都覆盖。
- **知识点不限制重复次数**：同一 `skill_id` 可以关联多台真实机器，每个场景记录 `variant_id` 与明确的教学增量。
- **现有标签不自动成为细分技能已验证**：目前旧机器清单的 `validated_skills` 是历史 CI 关联证据，具体技能还需对应单独断言。新技能表默认 `not_audited`，避免虚报。
- **难度属于整道题的玩家体验**：每条知识点的 `first_target_level` 只是适合第一次练习的深度，技术可以重复出现在更高等级。
- **一台机器有一个主专题、若干次要知识点**；统计专题覆盖只按主标签，统计技能训练按真实有证据的场景变体。

参考：[PortSwigger 官方 31 专题](https://portswigger.net/web-security/all-topics)、[所有学习资料](https://portswigger.net/web-security/all-materials)、[选题评审与真实机器候选](#选题评审与真实靶机候选)。完整结构化目录：[**219 个目标**](../catalog/web-competencies.json)。

#### 二、按照官方专题逐一编入题库

这里列出 **31 个专题**（14 服务端、6 客户端、11 进阶），每个专题已分解成可以独立验收的具体目标。表中的数字是**规划中的知识目标数量**，不是已完成的靶机数量。

#### 服务端专题 (14)

| 专题 | 知识目标 | 例：从基础到进阶 |
| --- | ---: | --- |
| [SQL injection](https://portswigger.net/web-security/sql-injection) (`sqli`) | 15 | SQL 查询逻辑与认证绕过 → 条件错误型盲注 → 多语句执行与权限边界 |
| [Authentication vulnerabilities](https://portswigger.net/web-security/authentication) (`auth_session`) | 9 | 逻辑错误绕过登录 → 密码修改流程权限错误 → 会话固定与登录状态切换 |
| [Path traversal](https://portswigger.net/web-security/file-path-traversal) (`file_read`) | 9 | 基础目录遍历读取文件 → 预期目录前缀校验绕过 → 文件读取、包含到执行的多阶段链 |
| [OS command injection](https://portswigger.net/web-security/os-command-injection) (`command_injection`) | 7 | 基础 shell 命令执行 → 环境变量/PATH 影响原生命令 → 引号/转义/过滤环境下的上下文突破 |
| [Business logic vulnerabilities](https://portswigger.net/web-security/logic-flaws) (`business_logic`) | 6 | 业务步骤顺序绕过 → 优惠券/奖励重复兑换 → 多个业务动作组合造成权限/资金错误 |
| [Information disclosure](https://portswigger.net/web-security/information-disclosure) (`information_disclosure`) | 6 | 详细错误与调试页面泄露 → 源码映射/前端包中隐藏信息 → 信息泄露联动认证及后续攻击 |
| [Access control](https://portswigger.net/web-security/access-control) (`idor`) | 7 | 直接对象引用越权（IDOR） → 角色参数或头部信任问题 → 跨租户/组织级对象隔离 |
| [File upload vulnerabilities](https://portswigger.net/web-security/file-upload) (`file_upload`) | 8 | 无限制文件上传 → 后缀解析器/服务器处理差异 → 其他 HTTP 上传方法与接口 |
| [Race conditions](https://portswigger.net/web-security/race-conditions) (`race_conditions`) | 6 | 检查与使用分离（TOCTOU） → 多个不同端点协调竞争 → 跨账户并发额度竞争 |
| [Server-side request forgery (SSRF)](https://portswigger.net/web-security/ssrf) (`ssrf`) | 9 | 服务端请求本机资源 → 开放重定向绕过目标限制 → 跨后端/协议的多阶段内部服务链 |
| [XML external entity injection (XXE)](https://portswigger.net/web-security/xxe) (`xxe`) | 7 | 外部实体读取本地文件 → 无回显 XXE 带外验证 → 不同 XML 解析配置边界 |
| [NoSQL injection](https://portswigger.net/web-security/nosql-injection) (`nosql`) | 6 | JSON 查询操作符认证绕过 → 条件型数据推断 → 输入结构/过滤与数据库语义差异 |
| [API testing](https://portswigger.net/web-security/api-testing) (`api_testing`) | 7 | 隐藏 API 端点与路径发现 → 隐藏字段与参数探测 → API 对象授权与跨服务边界 |
| [Web cache deception](https://portswigger.net/web-security/web-cache-deception) (`cache_deception`) | 5 | 伪静态扩展名欺骗缓存 → 缓存与后端 URL 规范化不一致 → 跨用户缓存污染与数据读取 |

#### 客户端专题 (6)

| 专题 | 知识目标 | 例：从基础到进阶 |
| --- | ---: | --- |
| [Cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting) (`xss`) | 12 | 基础反射型 XSS → DOM sources 与 sinks → 由浏览器脚本完成跨用户权限操作 |
| [Cross-site request forgery (CSRF)](https://portswigger.net/web-security/csrf) (`csrf`) | 8 | 无防护状态修改请求 → SameSite 规则和跨站请求差异 → XSS 与 CSRF 跨上下文组合 |
| [Cross-origin resource sharing (CORS)](https://portswigger.net/web-security/cors) (`cors`) | 5 | 任意 Origin 回显和敏感数据暴露 → 误信可控制的子域来源 → 动态 CORS 头与缓存相互影响 |
| [Clickjacking](https://portswigger.net/web-security/clickjacking) (`clickjacking`) | 4 | 无 X-Frame-Options/frame-ancestors 的嵌入 → 多步骤 Clickjacking → Clickjacking 与状态更改组合 |
| [DOM-based vulnerabilities](https://portswigger.net/web-security/dom-based) (`dom_vulnerabilities`) | 8 | DOM 输入来源与危险 sink 的识别 → DOM-based cookie 操作 → 浏览器模板动态执行 |
| [WebSockets](https://portswigger.net/web-security/websockets) (`websockets`) | 5 | WS 连接、协议与消息结构探测 → WS 消息渲染注入 → WebSocket 承载的盲注或跨协议数据提取 |

#### 进阶专题专题 (11)

| 专题 | 知识目标 | 例：从基础到进阶 |
| --- | ---: | --- |
| [Insecure deserialization](https://portswigger.net/web-security/deserialization) (`deserialization`) | 7 | 不安全反序列化输入识别 → 真实依赖库 Gadget → PHP/Java/Ruby/Node 解析行为差异 |
| [Web LLM attacks](https://portswigger.net/web-security/llm-attacks) (`web_llm`) | 6 | 直达提示注入与指令混淆 → LLM 可调用的内部 API 滥用 → AI 驱动扫描器触发后续漏洞 |
| [GraphQL API vulnerabilities](https://portswigger.net/web-security/graphql) (`graphql`) | 6 | GraphQL Schema introspection → 别名/批处理引发的限流与验证差异 → 深度/复杂度与资源限制 |
| [Server-side template injection](https://portswigger.net/web-security/server-side-template-injection) (`ssti`) | 6 | 基本模板表达式注入 → 真实模板执行环境中的权限变化 → 模板回显受限时的证明与提取 |
| [Web cache poisoning](https://portswigger.net/web-security/web-cache-poisoning) (`cache_poisoning`) | 6 | 缓存键与可观测命中发现 → 缓存规范化差异 → 跨用户共享缓存投毒效果 |
| [HTTP Host header attacks](https://portswigger.net/web-security/host-header) (`http_host`) | 5 | Host 与转发主机头的输入面 → 基于 Host 的内部路由或限制绕过 → Host 注入与缓存联动 |
| [HTTP request smuggling](https://portswigger.net/web-security/request-smuggling) (`request_smuggling`) | 9 | 双 HTTP 解析器/网关模型 → HTTP/2 降级引发歧义 → 浏览器驱动的客户端 desync |
| [OAuth authentication](https://portswigger.net/web-security/oauth) (`oauth`) | 6 | OAuth 授权码与回调模型 → 第三方账户绑定错误 → OIDC 发现、nonce 和 ID Token 验证 |
| [JWT attacks](https://portswigger.net/web-security/jwt) (`jwt`) | 6 | 签名与声明验证边界 → 非对称与对称算法混淆 → JWK/jku 信任锚选择错误 |
| [Prototype pollution](https://portswigger.net/web-security/prototype-pollution) (`prototype_pollution`) | 7 | JavaScript 原型链理解与可变属性 → 前端框架 Gadget 与 sink → 过滤/无效化机制绕过 |
| [Essential skills](https://portswigger.net/web-security/essential-skills) (`essential_skills`) | 6 | Burp Proxy 与 Repeater 基础 → Intruder 枚举与差分观察 → 重现性、对照请求与证据记录 |

#### 三、SQL 注入：按机制而不是“注入题数量”统计

如下 15 个目标必须分别考虑；多个数据库、不同请求入口和不同响应反馈可以给同一目标增加更多机器。当前 Union、Validation、Pebbles、GoodGames **并不等于**所有 SQLi 目标已验收。

| `skill_id` | 首次建议等级 | 独立训练目标 |
| --- | --- | --- |
| `sqli.auth-bypass` | 初级 | SQL 查询逻辑与认证绕过 |
| `sqli.where-hidden` | 初级 | WHERE 条件中的隐藏数据获取 |
| `sqli.union` | 初级 | UNION 可见数据回显 |
| `sqli.union-column-count` | 中级 | UNION 列数探测 |
| `sqli.union-type` | 中级 | UNION 数据类型与拼接输出 |
| `sqli.db-enumeration` | 中级 | 数据库版本、表与列枚举 |
| `sqli.error-based` | 中级 | 显式数据库报错提取 |
| `sqli.conditional-error` | 中级 | 条件错误型盲注 |
| `sqli.boolean-blind` | 中级 | 布尔差异盲注 |
| `sqli.time-blind` | 中级 | 时间差异盲注 |
| `sqli.second-order` | 中级 | 二阶注入与后续消费点 |
| `sqli.file-operations` | 中级 | 数据库文件读取与写入 |
| `sqli.oast` | 高级 | 异步带外探测与数据带外获取 |
| `sqli.filter-bypass` | 高级 | 不同编码/上下文的过滤绕过 |
| `sqli.stacked-query` | 高级 | 多语句执行与权限边界 |

举例：可以同时保留 Union 的真实 MariaDB `UNION/LOAD_FILE`、Validation 的二阶 SQLi，再做一台 Cookie 布尔盲注、一台 PostgreSQL 时间盲注，以及 Soccer 风格的 WebSocket 布尔盲注。这些不是“只是换个名字”的重复。

#### 四、XSS：必须区分浏览器上下文

**JavaScript 实际在浏览器中执行，或成功完成受害者页面内的指定权限操作，才算验收。** 只检查 HTTP 响应含字符串、存在 CSP 头部或写入了 XSS payload，都不算技术已覆盖。

| `skill_id` | 首次建议等级 | 独立训练目标 |
| --- | --- | --- |
| `xss.reflected` | 初级 | 基础反射型 XSS |
| `xss.reflected-html` | 初级 | HTML 文本节点上下文 |
| `xss.reflected-attribute` | 中级 | HTML 属性上下文 |
| `xss.reflected-js` | 中级 | JavaScript 字符串/模板上下文 |
| `xss.reflected-url` | 中级 | 链接/URL 属性上下文 |
| `xss.stored` | 初级 | 存储型 XSS |
| `xss.dom` | 中级 | DOM sources 与 sinks |
| `xss.client-template` | 中级 | 客户端模板注入触发脚本 |
| `xss.filter-bypass` | 高级 | 编码/标签/事件过滤约束 |
| `xss.csp-bypass` | 高级 | 有效 CSP 存在时的约束绕过 |
| `xss.blind` | 高级 | 管理员浏览器触发 Blind XSS |
| `xss.cross-user-action` | 高级 | 由浏览器脚本完成跨用户权限操作 |

当前仓库的 Cursed Stale Policy 有 CSP/XSS 相关代码，但**尚无可信的完整浏览器攻击链验收**；不能因为它存在就把 CSP 绕过和 Blind XSS 标成“已覆盖”。真实管理员 Bot 必须在隔离网络中执行，管理员 Cookie/Session 不能通过测试脚本假装被窃取。

#### 五、SSRF 与路径遍历：同一个名称仍可有多种深入情景

| 知识模块 | 基础训练 | 中级变体 | 高级变体 |
| --- | --- | --- | --- |
| SSRF | 本机回环 API、真实服务器端请求 | 内网端口枚举、重定向、黑名单 | URL 解析器差异、OAST、跨服务链 |
| 路径遍历 / LFI | 文件读取与相对路径 | 绝对路径、嵌套剥离、双重解码、前缀/后缀限制 | LFI 包装器、文件到 RCE 的多阶段链 |

Editorial 已对 SSRF 基本与内网 API 访问做了完整攻击链 CI，但**不代表** URL 校验绕过、Blind SSRF 或多协议组合已完成。Trick 与 Inject 是不同 LFI/路径遍历综合链的候选，必须经过真实源码/Writeup 评审才进入开发。

#### 六、初级、中级、高级：难度用什么判定

| 级别 | 真实玩家面对的场景 | 不是判定依据 |
| --- | --- | --- |
| **初级** | 单一机制、清楚但不直白的线索，基础枚举与请求调试，能从正常应用自然发现入口 | 不是因为只存在一个 Flag，也不是非要无认证 |
| **中级** | 多页面或角色、不同数据/回显上下文、盲注/安全限制、简单凭据转移与系统权限 | 不是仅因某个 CVE 在年份较旧或需要 SSH |
| **高级** | 多协议、盲/OAST 反馈、真实浏览器安全策略、解析器/缓存/竞态边界、多个独立限制的组合 | 不是单纯增加密码、把目录名藏得更深或增大镜像 |

高级专题组中的 JWT、OAuth 或 Request Smuggling 也有适合初学者的底层概念；**`first_target_level` 是该细分目标首次训练的建议级别，并不限制后续复练难度。**

#### 七、覆盖状态：专题 → 技能 → 场景 → 实际验收

一个场景至少记录以下信息（主清单中的每台机器在后续 PR 逐步补齐）：

```json
{
  "topic_id": "sqli",
  "skill_id": "sqli.boolean-blind",
  "variant_id": "cookie-mysql-boolean-no-error-v1",
  "level": "intermediate",
  "source_lab": "待原始资料核查",
  "input_surface": "cookie",
  "feedback": "boolean-difference",
  "technology": ["php", "database-mysql"],
  "constraint": ["no-direct-query-output"],
  "lab_ci_status": "not_verified",
  "evidence": null,
  "worker_status": "not_verified"
}
```

该 JSON 是**字段结构示例，不是已存在的实际靶机**。现实中只有提供可重放的独立测试和具体证据，才能将场景标记 `lab_verified`。重复同一技能的机器使用不同 `variant_id`，明确差异。

#### 绝不能混淆的状态

1. `cataloged`：专题/技能已列入计划。
2. `researching`：已找到候选 HTB/OffSec/开源应用，但原始行为、版本和完整链未核实。
3. `implemented`：真实源码和配置已提交，未完整验收。
4. `lab_ci_verified`：旧版历史 CI 状态，保留其原运行证据；未来完整流程改由每台 Lab 的 `e2e_ci_status`、工作流链接与提交 SHA 记录。**不会因为某台综合机器的 CI 通过就自动让每个关联技能通过。**
5. `worker_verified`：真实平台 Worker 的镜像启动、私有网络、资源隔离和多用户调度通过；**Worker 不判题、不管理 Flag、不提供 XSS 管理员 Bot**。Flag 由靶机经真实利用提供，答案由 Web 后端 `attemptChallenge()` 校验。详见 [平台与 Flag 责任边界](#平台-flag-与管理员-bot-责任边界)。

#### 八、如何维护

- 下一台靶机先读 [选题方法](#选题评审与真实靶机候选)，确认 `topic_id` + `skill_id` + 有意义的 `variant_id`，**允许同一知识点再做很多次**。
- 所有新类别、技能及三个难度入口统一更新 [`web-competencies.json`](../catalog/web-competencies.json)。原 `web-curriculum.json` 保存现有机器、历史 CI 记录与滚动开发队列。
- 保留原始上游代码及版本；没有确切源码时可重建可观察网站行为，但不得将模拟程序伪装成真实漏洞。
- 新的 Web 专项不强制一枚 User + 一枚 Root，综合靶机则要分别验收其原始目标。
- 参考 [仓库路线图](#滚动开发路线与知识缺口) 的动态优先级，**不再规定只做九台**。

## 滚动开发路线与知识缺口


更新：2026-11-23。**选题依据是 PortSwigger 式的细分知识点和不同真实利用场景，不是“每种漏洞三台”“做满九台就停止”。**

先看：[31 专题 / 219 知识目标](../catalog/web-competencies.json) → [分类与难度](#技术分类与训练梯度) → [候选机器与评分方法](#选题评审与真实靶机候选) → [机器及滚动队列](../catalog/web-curriculum.json)。

#### 一、历史存量快照：17 个目录（Web 16 + 非 Web 服务链 1；非当前完整清单）

**以下表格保留 2026-11-23 的历史目录快照与当时的 CI 证据**，仅用于追溯。当前 27 台 Lab 的状态请看 [现有 main 靶机清单](EXISTING_WEB_LAB_RELEASE_INVENTORY.md) 和 [结构化主清单](../catalog/web-curriculum.json)。

| 靶机 | 暂定级别 | 主要训练类别 | 典型场景差异 | 验收状态 |
| --- | --- | --- | --- | --- |
| base | 初级 | 认证与会话安全 | 原生文件上传 | 尚无完整验收 |
| bashed | 初级 | 暴露的管理或执行接口 | Web shell | 完整目标链 CI（非 Worker） |
| bike | 初级 | 模板注入 | 模板上下文 | 局部/目标未全验收 |
| bountyhunter | 中级 | XML 外部实体 | 真实外部实体 | 完整目标链 CI（非 Worker） |
| cap | 中级 | 对象级授权与 IDOR | 越权获取其他人的网络流量 | 完整目标链 CI（非 Worker） |
| cursed-stale-policy | 高级 | 跨站脚本 | 管理员浏览器 / CSP | 尚无完整验收 |
| devvortex | 中级 | CMS / 应用组件漏洞 | CVE-2023-23752 配置泄露 → Joomla 模板编辑 | Web-only 单 Flag，独立攻击端 E2E 已通过 |
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

#### 二、每个知识点的“覆盖”要怎么计算

以 [catalog/web-competencies.json](../catalog/web-competencies.json) 的 219 个目标为索引，每个目标关联 0..N 条场景变体、每个变体关联 0..N 台真实靶机。

长期维护 3 个不同指标：

1. **知识点覆盖**：多少个 skill_id 存在针对其机制的实际成功验收证据？不是只要在 README 提过就算。
2. **场景深度**：同一 skill_id 在多少个**实质不同**的输入面、反馈模式、数据库/框架、校验约束、浏览器/协议边界下训练过？同点重复**可以加分**。
3. **梯度完整性**：该技能在初级、中级和高级场景是否分别有适宜学习任务？不要求每项强行做三台，但核心知识点要有向上递进路径。

**最重要的规则：不限机器数量。** 即使当前 SQLi 已有四台，只要新机器能训练真实布尔盲注、时间盲注、XML 编码绕过、WebSocket、PostgreSQL 方言等新变体，都可以继续选择。

#### 三、SQLi：具体在哪些方向重复才有价值？

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

#### 四、XSS：目前核心短板，按浏览器上下文建立递进

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

#### 五、其余 29 个专题都必须进入计划，而不只是 SQLi/XSS

其它技能也已经完整编目，以下列出当前选题方向（详细子目标见 JSON）：

| 方向组 | 候选训练技术 |
| --- | --- |
| 服务端核心 | Authentication、Path traversal/LFI、Command injection、Business logic、Information disclosure、Access control、File upload、Race conditions、SSRF、XXE、NoSQL injection、API testing、Cache deception |
| 客户端 | CSRF、CORS、Clickjacking、DOM-based、WebSockets |
| 进阶 | Deserialization、Web LLM、GraphQL、SSTI、Cache poisoning、Host header、Request smuggling、OAuth、JWT、Prototype pollution、Essential skills |

其中初级题并非必然来自官方 Server-side 组。JWT、GraphQL 或 Prototype pollution 也需要基本概念题，而高级 SSRF/SQLi 需要更强限制和复杂反馈。**题目类型、难度、知识点是三个独立维度**。

#### 六、持续滚动的下一批选题：不设固定九台上限

当前 [web-curriculum.json](../catalog/web-curriculum.json) 记录 **33 条待开展的技能/场景需求**；这不是 33 台机器的开发承诺，也不是所有需要覆盖的 219 个技能的终点。

| 滚动优先组 | 预期知识目标 | 实物候选或来源约束 |
| --- | --- | --- |
| **基础概念与浏览器** | 反射 XSS 的 HTML/属性上下文、基础路径遍历、NoSQL 操作符查询 | XSS 优先采用 Vulhub Django CVE-2017-12794，随后可做轻量 WonderCMS；不需要打包整套 Juice Shop |
| **SQLi 递进** | 条件响应、报错、时间盲注、带外与不同数据库方言 | 可重复选 SQLi 综合靶机；Soccer 的 WebSocket 盲注与 Union 的 UNION 不是重复训练 |
| **浏览器/会话进阶** | 存储/DOM/Blind XSS、CSP、CSRF、JWT、OAuth | Headless 是 Blind XSS 候选；Cursed 需先独立验证 |
| **实际应用组件** | NoSQL + 反序列化、LFI + 真 CVE、Ruby PDF 转换 | NodeBlog、Trick、Inject、Precious，必须逐一核实原版软件版本 |
| **协议与高复杂度** | WebSocket、Race、API/GraphQL、Request Smuggling、Cache、Prototype pollution、LLM | 要有真实解析器、代理、数据库、浏览器/代理环境与独立测试 |

#### 现已找到正式页面的机器候选（尚未批准开发）

轻量优先：**Django 1.11.4 调试页面 XSS（Vulhub）、WonderCMS 3.4.2、HTB Alert**；细节见 [选题评审](#选题评审与真实靶机候选)，不把源代码不足或 Bot 环境复杂的题目当作已验收。

| HTB 机器 | 公开资料支持的典型链 | 规划中的增量价值 |
| --- | --- | --- |
| [Headless](https://www.hackthebox.com/machines/headless) | Python Werkzeug、Blind XSS 经管理员浏览器 | User-Agent + 管理员 Bot，补 XSS 较深场景 |
| [Trick](https://www.hackthebox.com/machines/trick) | DNS/vhost、SQLi 文件读、LFI | 多站点真实发现，路径遍历/LFI/SQLi 不同组合 |
| [NodeBlog](https://www.hackthebox.com/machines/nodeblog) | Node/Express、NoSQL、反序列化线索 | 真实 MongoDB/序列化栈，与 SQLi 区分 |
| [Precious](https://www.hackthebox.com/machines/precious) | Ruby/PDFKit、YAML 处理 | 引入不同语言的反序列化与依赖漏洞 |
| [Soccer](https://www.hackthebox.com/machines/Soccer) | Tiny File Manager、WebSocket SQL 盲注 | WS 数据通道、盲注反馈、多阶段 Linux 提权 |
| [Inject](https://www.hackthebox.com/machines/inject) | 上传中的 LFI → Spring Cloud Function | Java 栈 LFI 与真实 CVE，区别于 PHP |

更完整的十四台候选与量化评审标准请看 [WEB_MACHINE_SELECTION.md](#选题评审与真实靶机候选)。正式开发时仍须查证 Writeup/源码，确定版本，并且不能声称未公开的原题源码可得。

#### 七、如何选择与提交下一台

1. **先选知识目标**：web-competencies.json 里的一个或多个 skill_id，并给出初/中/高级的场景深度。
2. **允许重复，但需有学习增量**：明确输入面/反馈/约束/技术栈/侦察/目标至少一项实质变化；记录 variant_id。
3. **再找原版资料**：HTB/OffSec 题、历史 Writeup、漏洞公告和上游项目；优先真实存在的原版易受影响组件。
4. **按选题规则评分**：来源真实性、知识差异、侦察自然性、人工可复现性、Docker 约束、镜像资源；原则上不少于 75/100，硬性不合规则不准开发。
5. **单机单 PR**：按原题实现真实组件；CI 检查构建、启动和健康，并由独立攻击端自动完成题目目标与 Flag 验收。先展示 diff 与实际检查结果，取得批准后才创建、更新或提交 PR。
6. **区分发布**：源码进入 main 和实验室 CI 通过，都不是 Worker 发布许可；未验证的场景保持未验证。
7. **持续更新知识点**：端到端 CI 成功后在目标技能下新增已验证的 variant_id 与对应运行证据；基础 CI 成功不自动改变技能验收状态。

#### 八、下次续作约定

下次用户说“继续制作靶机”，先读取本文件、[分类](#技术分类与训练梯度)、[选题](#选题评审与真实靶机候选) 与两个 catalog/*.json，再比较 main、已合并 PR 与新 CI，选择适合的真实案例。

**最关键的变化：题库既要横向全覆盖 Web 安全技术，又要纵向让同一个知识点从入门到复杂场景反复出现。选题服务于知识点，而不是知识点迁就手头的靶机。**

## 选题评审与真实靶机候选


版本：2026-11-23 / v2。**本文件解决“知道缺哪个知识点，但不知道该选哪台机器”的问题。**

配套：
- [31 个官方专题、219 个自编知识目标](../catalog/web-competencies.json)
- [现有 17 台机器及选题队列](../catalog/web-curriculum.json)
- [知识点与三级难度](#技术分类与训练梯度)
- [滚动路线图](#滚动开发路线与知识缺口)

#### 1. 不排除重复：只排除“没有增量的重复”

**同一 SQLi、XSS、SSRF 可以安排任意多台靶机。** 不以“已有 SQLi 4 台”否决新的 SQLi。真正要回答的是：

1. **教什么**：对应哪个 `topic_id` 和 `skill_id`？玩家做完能独立完成的操作是什么？
2. **如何发现**：玩家最先看到什么页面/服务？必须经过哪些侦察与枚举，不能直接在首页标注漏洞位置。
3. **与已有机器有何区别**：以下至少存在一项**有学习意义、且验收可证明**的差异，而不仅是换 UI/Flag/名字：
   - 输入面：GET / POST / Cookie / JSON / XML / 上传 / HTTP header / WebSocket / API；
   - 核心机制：UNION、二阶、布尔盲注、时间盲注、OAST、模板/浏览器执行；
   - 约束：黑白名单、编码、解析差异、权限、CSP、SameSite、并发窗口；
   - 技术栈：MySQL / PostgreSQL / SQLite / MongoDB；PHP / Java / Node / Ruby / Python；
   - 侦察链：普通目录、vhost、DNS、API 文档、Git 历史、浏览器 JS；
   - 目标：文件读取、权限绕过、业务操作、Foothold、User/Root Flag；
   - 独立复现条件：浏览器、管理员 Bot、两个前后端 HTTP 解析器、时钟/并发、独立 OAST 接收端。
4. **是否真实**：是否有可信历史 Writeup，是否能固定上游真实受影响版本和漏洞执行路径？
5. **能否工程化**：Docker Linux 私网可运行、小镜像、健康检查、隔离、实例重置、基础 CI、独立攻击端端到端验收与 Worker 兼容。

同一个 `skill_id` 的第二台机器应具有 `variant_id` 和上述差异说明；同一技能可以有多个 `variant_id`，绝不设“一个点最多一题”或“每类最多三台”。

#### 2. “专项”与“综合”分别挑选

| 类型 | 选题标准 | 可接受的目标 |
| --- | --- | --- |
| Web 知识专项 | 一种细分机制讲清楚；真实浏览器/数据库/协议栈，可从普通页面自然发现 | 单 Flag、业务状态改变、权限获取或可观测证据，不强制添加系统 Root |
| Web 综合靶机 | 原始侦察 → 真实 Web 漏洞 → 凭据/移动 → SSH/User → 原生 Linux 权限提升/Root | 依据原题是否双 Flag，避免凭空增加提权链 |
| 复合题 | 例如 SQLi + LFI、XSS + CSRF、SSRF + 内部 API；先明确**主要技能**，剩余标为次要技能 | 每一环有独立证明；难度按整个玩家路径定，不按漏洞个数定 |

#### 重复如何判定：以 SQLi 为例

| 机器/场景 | 可以同时存在吗 | 不同的知识目标 |
| --- | --- | --- |
| Union（已有） | 可以 | MySQL/PHP UNION + FILE + HTTP header/SSH |
| Validation（已有） | 可以 | 二阶注入：先存储参数，再由另一请求消费 |
| Pebbles（已有） | 可以 | 真实 ZoneMinder，SQLi → 数据库文件与 UDF 影响 |
| 另一台 Cookie 布尔盲注 | **应该加入** | 没有直接回显，需要比较响应推断数据 |
| 另一台 PostgreSQL 时间盲注 | **应该加入** | 不同数据库语法、延时噪声与统计 |
| Soccer（候选） | **应该加入** | WebSocket 帧传输、盲 SQLi 与跨协议链 |
| 又一台普通 PHP UNION 登录 | 可以，但**低于前述优先级** | 只有在输入环境、数据库或约束不同、确有教学增量时才选 |

#### XSS 不能只看“弹窗”

至少分别覆盖：HTML 正文、HTML 属性、JavaScript 字符串、DOM source/sink、存储型、管理员浏览器 Blind XSS、CSP 真正生效下的限制、浏览器内执行导致权限操作。**这些可以由多台机器重复交叉练习。**

#### 3. 候选机器评审表（100 分）

| 维度 | 权重 | 评分方法 |
| --- | ---: | --- |
| 原始证据与组件真实性 | 25 | 官方机器页 + ≥1 可核实 Writeup + 上游受影响版本/源码；不允许伪造漏洞 |
| 相比已有机器的知识增量 | 20 | 不同技能、输入面、反馈、约束/技术栈或新边界 |
| 侦察链的合理性 | 20 | 真实页面/服务、信息隐藏自然、无把漏洞参数直接告诉玩家 |
| 独立验收的可复现性 | 15 | 攻击容器可验证真实效果；有版本/权限/重置对照证据 |
| Linux Docker 的真实可移植性 | 15 | 无宿主机逃逸、无 --privileged、隔离与 Worker 能力清楚 |
| 构建体积及运行资源 | 5 | 有基础镜像和资源方案；昂贵服务能否简化而不损失漏洞 |
| **合计** | **100** | 建议 ≥75 才进入实际开发（需要有依据的评审分数） |

**硬性否决项**：模拟漏洞处理器替代真漏洞、伪造 Root/Flag 成功、需要主机逃逸、不可靠的依赖或非法素材、唯一攻击链无法在隔离环境复现。硬性否决无论评分多少都不能放行。

#### 评审时必须写的 `candidate_review`

- `source`：HTB/OffSec 原题 URL、Writeup、公开代码 URL；是否原版源码？
- `upstream`：软件/依赖/协议的具体受影响版本；补丁前后的差异。
- `route`：侦察 → 漏洞 → 获取能力 → 目标 Flag 的完整玩家路径。
- `knowledge`：主 `skill_id`、次要 `skill_id`、难度、先修技能。
- `variant`：和现有机器相比具体新增什么；输入面/反馈/约束/栈至少一项有意义的不同。
- `container`：真实需要的服务、典型 RAM/镜像目标、端口、capability、禁止 host 权限的实现。
- `acceptance`：独立容器看到的 HTTP/浏览器/协议证据、真实 UID、Flag 与重置。
- `risk`：未公开的源代码需要重建哪些可观察行为？哪些细节尚未证实？
- `decision`：`researching` → `source_verified` → `feasible` → `in_progress` → `lab_ci_verified` → `worker_verified`。

#### 4. 已有公开证据的真实机器候选（不是制作承诺）

下表是**选题候选**，要先再审具体 Writeup、依赖版本、许可证和 Docker 工程可行性。官方所标难度仅供参考，trytopwn 难度要按自身体验另评估。

| 候选机器（官方/历史资料） | 适合补的知识点变体 | 需要保留的真实链 | 选题备注 |
| --- | --- | --- | --- |
| [HTB Headless](https://www.hackthebox.com/machines/headless) | `xss.blind`，管理员浏览器；HTTP User-Agent 输入面 | 支持表单 → Blind XSS → 管理员会话 → 命令注入 | **中高优先**；必须有真实管理员浏览器，不可硬编码 cookie |
| [HTB Trick](https://www.hackthebox.com/machines/trick) | `file_read.nested-traversal`，`sqli.file-operations` | DNS/vhost → SQLi/读取配置 → LFI → SSH → fail2ban | **高优先**；多服务内存/时间成本需审查 |
| [HTB NodeBlog](https://www.hackthebox.com/machines/nodeblog) | `nosql.operator-auth-bypass`，`deserialization.unsafe-parse` | Express + MongoDB 操作符、真实 XML 解析与 node-serialize | **高优先**；必须使用原始危险依赖及真实 DB |
| [HTB Precious](https://www.hackthebox.com/machines/precious) | `deserialization.unsafe-parse`，Ruby/YAML | PDFKit 文件转换 → Ruby 凭据 → YAML 反序列化 | **高优先**；保留真实 PDF 转换而非模拟返回 |
| [HTB Soccer](https://www.hackthebox.com/machines/Soccer) | `websockets.blind-sqli`，`sqli.boolean-blind` | Tiny File Manager → WS 盲注 → SSH → doas/dstat | **高优先**；不是普通 PHP UNION 的重复 |
| [HTB Inject](https://www.hackthebox.com/machines/inject) | `file_read.lfi`，Java 组件漏洞 | 上传功能的 LFI → 真实 Spring Cloud Function → SSH/Ansible | Java 内存、漏洞版本与原版环境必须核实 |
| [HTB Zipping](https://www.hackthebox.com/machines/zipping) | `file_read.path-traversal`，`file_read.file-to-rce` | ZIP 符号链接文件读取 → SQLi → LFI/执行 | 与普通 PHP 文件上传区别明显 |
| [HTB Codify](https://www.hackthebox.com/machines/codify) | **补充专题** JavaScript vm2 沙箱逃逸 | JS 测试器 → 真实 vm2 → SQLite → Bash | 属于应用沙箱，不是 Docker 容器逃逸；不是 XSS |
| [HTB Shared](https://www.hackthebox.com/machines/shared) | Cookie 输入面 SQLi | Cookie SQLi → 真实后续服务利用 | 与常规表单 SQLi 场景不同；后续细节待核对 |
| [HTB Gavel](https://www.hackthebox.com/machines/gavel) | PHP PDO SQLi 与 YAML 解析链 | PDO 错用 → PHP 代码执行 → YAML/后台工作流 | 中高级候选，重点审查版本与 Worker 隔离 |

候选有的已具备官方机器概要，有的后续仍需 Writeup 和源码对照；本文件不将它们写为已验证、在制作或已经满足 Docker 约束。

#### 5. 实际制作顺序：持续滚动，不以“9 台完成”为终点

1. 先检查 [细分知识目录](../catalog/web-competencies.json) 中尚无独立测试的目标，并确定场景变体；**优先补薄弱基础，但不限制重复数量**。
2. 对比上表的公开候选，选择最容易核实真实技术、侦察真实且 Docker 可行的一台；必要时对同一知识点选多台不同复杂度。
3. 只为选中的机器创建开发 PR；更新 [主清单](../catalog/web-curriculum.json) 的 `backlog`，在 PR 中放入 `candidate_review`。
4. 先通过靶机专属的外部入口 → 利用 → 目标 Flag/权限 CI；记录运行镜像字节数、内存、隔离和重置。
5. 再单独确认 Worker 的网络、权限与多用户资源调度；Flag 的出现路径由靶机负责，正确性由 Web 后端校验，Worker 不参与判题。对需要管理员浏览器的 XSS，浏览器与审阅流程由题目自身设计，不是 Worker 的业务。详见 [职责边界](#平台-flag-与管理员-bot-责任边界)。

**选题优先级 = 缺少的知识训练价值 + 与已有靶机的有意义差异 + 真实可复现性，不是“这个漏洞已有 1 台所以禁止再选”。**

#### 6. 小型 XSS 靶机候选（2026-11-23 增补）

优先使用小型、真实受影响的软件，**不推荐为单一 XSS 技能打包整个 Juice Shop**。这里区分两个易混名称：VulnHub 是可下载的完整虚拟机库；Vulhub 是按 CVE 提供 Docker 漏洞复现的项目。

| 选题优先 | 上游与可核实漏洞 | 预期训练能力 | 工程与教学限制 |
| --- | --- | --- | --- |
| 1：[Vulhub Django CVE-2017-12794](https://github.com/vulhub/vulhub/blob/master/django/CVE-2017-12794/README.md) | Django 1.11.4 在 DEBUG 500 页的真实 XSS；[官方依赖安全公告](https://github.com/advisories/GHSA-9r8w-6x8c-6jr9) | **初级**：反射型 XSS 与错误页的浏览器 HTML 上下文 | 仅复现原版 Django 错误页的特定触发条件，不伪装成普通搜索页漏洞；镜像体积须实测 |
| 2：[WonderCMS 3.4.2](https://github.com/WonderCMS/wondercms/releases/tag/3.4.2) | PHP/JSON 平面文件 CMS、真实 [CVE-2023-41425](https://github.com/advisories/GHSA-58rr-37rr-r6h5)，3.4.3 已修复 | **中级**：真实 XSS + 管理员操作 + 插件权限边界 | 不需数据库服务；必须证实原版输入上下文与实际管理员浏览器交互，不能只验证 JS 字符串 |
| 3：[HTB Alert](https://0xdf.gitlab.io/2025/03/22/htb-alert.html) | Markdown → 浏览器 XSS → 敏感文件读取 → SSH → Cron Root 的公开真实链 | **中级综合靶机**：跨用户浏览器行为与多阶段侦察 | 原站点源码未公开，重建时如实标明；需要管理员浏览器，Bot 运行资源单独测量 |
| 可选：[OWASP DSVW](https://vwad.owasp.org/app/damn-small-vulnerable-web-dsvw/) | 少于 100 行 Python 的教学源码 | **初级微型专项**：XSS/DOM 入门 | 尽管极小，但界面直接展示漏洞，不符合偏好自然侦察的综合靶机要求，不能硬称真实产品 CVE |

**历史选题记录（2026-11-25）**：当时曾将 HTB Intense 作为 SQLi 分类候选，目标为 SQLite 条件错误 Oracle → 管理员 Secret → SHA-256 LWT 长度扩展 → 管理员日志路径遍历 → Web Flag。该记录保留为历史规划，不覆盖后续已确认的 main 存量靶机优先顺序。

## 当前逐台制作顺序（2026-11-27）

当前按 main 存量清单逐台完成，不并行制作。已完成新标准 E2E 的是 Bike、Precious、GoodGames、Devvortex；Base 已完成双 Flag 完整 E2E；当前正在处理 **Trick**：复用现有多服务实现，只补独立 DNS/HTTP/SSH E2E 和随机双 Flag；Intense 暂缓，因其为高级 SQLi/密码学组合链。Devvortex 的范围为 Joomla 4.2.6 / CVE-2023-23752 Web-only 单 Flag，不包含 SSH、Apport 或 Linux Root 阶段。

执行细节与验收门槛以 [Lab Production Playbook](LAB_PRODUCTION_PLAYBOOK.md) 为准；状态与成功运行证据以 `catalog/web-curriculum.json` 为准。

## 平台 Flag 与管理员 Bot 责任边界


更新：2026-11-23。以实际 `10010100111000/attackbox` 的 `main` 分支代码为准，不要凭另一类 CTF 平台的架构猜测 Worker 的职责。

#### 已核对的代码边界

| 部件 | 负责什么 | 不负责什么 | 依据 |
| --- | --- | --- | --- |
| **Web 后端** | 持有题目与阶段答案，接受用户的 Flag 提交，比较答案并记录完成状态 | 不替代靶机内部真实漏洞，也不模拟漏洞利用 | `attackbox/web/server/api/challenges/[id]/attempt.post.ts`; `web/server/services/challenges.ts:attemptChallenge()`; `web/server/db/schema/challenges.ts:challengeStages.flag` |
| **Worker** | 镜像准备、实例启动/停止、资源限制、专用网络与容器生命周期；把收到的部署变量作为不透明环境变量转交给容器（如有配置） | **不进行 Flag 判题，不维护 XSS Bot，不决定什么时候“漏洞利用成功”** | `attackbox/worker/node/target_starts.go`; `worker/node/targets/model.go`; `worker/node/targets/engine.go` |
| **靶机容器** | 原版服务、真实漏洞、玩家通过漏洞发现或获取的 Flag（静态或实例级由题目自身处理） | 不在 Worker 中执行漏洞逻辑/判题 | 各 `labs/<name>/` 的原始版本、服务与验收逻辑 |

#### Flag 的推荐闭环

1. 题目配置明确一枚或多枚标准答案；**Web 后端**保存/校验提交的答案。
2. **Worker**只按 Web 发来的参数启动隔离靶机，若传入 Flag 环境变量也只是透明转交，**不解析 Flag、不参与正确性判定**。
3. 玩家通过真实漏洞从**靶机**取得对应 Flag；可直接在浏览器看到、通过文件读取、授权接口、程序响应、终端访问或跨浏览器交互获取。
4. 玩家把 Flag 输入平台的提交框，Web 后端完成判断。

**关于动态 Flag：** 当前 `challengeStages.flag` 是 Web 后端的静态阶段答案字段，不能因为靶机支持实例启动时注入变量，就宣称已经实现“每个实例自动轮换且服务器端同步判题”。如果某题真的启用实例级动态值，必须先明确 **Web 后端**如何维护正确答案与实例生命周期的关联；Worker 仍只转交 opaque 变量、调度实例，不承担判题。

#### Web Flag 的位置：优先融入真实业务数据，不要求本地文件

**Flag 是 Challenge 的完成标记，不是 Linux 文件读取任务。** 每道 Web 题应根据实际漏洞和业务对象决定 Flag 放在哪里；不要求所有题目都读取 `user.txt`、`root.txt` 或其他本地文件。

优先考虑真实应用已经存在的数据模型和响应位置：

| 漏洞/考点 | 可采用的 Flag 位置 | 学员通过什么取得 |
| --- | --- | --- |
| SQLi / NoSQLi | 数据库中的用户、文章、订单或配置记录 | 注入查询或数据推断 |
| IDOR / BOLA | 其他用户的私密资料、订单、附件元数据 | 越权读取对象 |
| Stored / Blind XSS | 管理员可见的工单、评论、消息或后台资料 | 真实浏览器中的脚本执行及目标操作 |
| CSRF | 受保护的账户设置或业务状态 | 真实受害者浏览器完成未授权操作；Flag 可显示在操作结果中 |
| SSTI | 模板上下文中的业务对象或配置值 | 真实模板表达式读取 |
| SSRF | 内部服务的真实响应数据 | 服务端请求到达内部服务并读取响应 |
| JWT / Session | 受保护 API 返回的用户/管理数据 | 验签、身份或会话处理缺陷 |
| Mass Assignment | 用户角色、账户属性或资源所有者字段 | 修改本不应由用户控制的属性，再访问真实受保护功能 |
| 文件上传 | 上传后被真实应用处理的文件、元数据或转换结果 | 上传解析/存储/处理漏洞 |
| XXE | XML 导入记录、应用配置或本地文件 | 实际 XML 外部实体解析 |

实施规则：

1. **先选自然业务位置，再决定 Flag 形式。** 如果漏洞目标是读取订单，就把 Flag 放在订单数据；如果目标是越权修改角色，就让 Flag 出现在该角色能够访问的真实管理功能中。不要为了统一而把所有 Flag 放进文件。
2. Flag 可以存在数据库记录、真实业务字段、应用配置、API 返回值、后台页面、模板上下文、上传文件或本地文件。以上都可以；选择应服务于题目目标。
3. 可以在真实应用的种子数据中增加专用记录/字段，或在初始化时将 CI 生成的随机 Flag 写入已有数据模型。不得为显示 Flag 新增伪造漏洞接口、模拟解析器或与应用无关的“取 Flag”端点。
4. Flag 不必严格防止从其他真实漏洞路径提前获得。优先保证预期解题路径真实、题目描述准确、答案与靶机数据一致；不要为了防绕题增加不必要的权限系统或架构复杂度。
5. 同一 Lab 的多道 Challenge 可以复用同一枚 Flag，也可以使用不同 Flag。后续综合题可以重复前置 Flag，数量按学习目标决定。
6. 静态 Flag 由 CI/发布版本生成器与靶机种子数据、Challenge Markdown 答案保持同源；同一版本重建必须复用同一组值。Web 后端负责判题，Worker 不负责生成或校验 Flag。
7. 只有当题目本身考察路径遍历、LFI、XXE 文件读取或命令执行后的文件读取时，才把本地文件作为主要 Flag 位置。不能因为传统 HTB Machine 常用 `user.txt` 就把这个习惯强加给纯 Web 题。

#### XSS 靶机选择：不要强加 Bot

XSS 是**浏览器端**漏洞，不代表每道 XSS 都必须有模拟管理员：

- **基础反射型 XSS**：允许选择真正具有公开入口的原版脆弱应用，玩家在自己的浏览器触发真实 JS；若设计单 Flag，奖励规则应与具体学习目标相称，不在 Worker 放任何审核器。
- **管理员上下文 / Blind XSS**：如果目标是读取**其他人的管理员信息**，必须有真实受害者浏览器访问过程，否则玩家没有管理员会话，无法仅凭自己的浏览器获得管理员权限。需要该机制时，属于**靶机自身的完整业务环境和测试/审阅服务**，不是 Worker 的通用能力。
- **不可取的捷径**：把本应管理员专属的 Flag 放到任何访客可调用的 URL，或仅根据 payload 字符串包含 `<script>` 就返回 Flag。这使玩家完全无需执行 XSS，属于伪造验收/绕题捷径。
- 如果单容器部署和小镜像的要求与浏览器受害者场景冲突，应当**调整靶机选择或题型定位**，而不是要求 Worker 长出 XSS 业务逻辑。当前 Worker 的 target 定义和 DockerEngine 均按单个目标容器处理；改架构前不要默认能附加 Sidecar。

#### WonderCMS PR #12 的边界

WonderCMS 3.4.2 **原版反射型属性 XSS 已通过真实 Chromium CI**。但是目前自动测试在 CI 中先手动登录 CMS 的管理员，然后验证漏洞；`/review-proof.php` 是管理员会话专用目标。

这不等于普通玩家已经能独立获取 Flag。对当前 *管理员上下文中级题*：

- 要么给靶机设计**自身**的可复现受害者访问流程和出题目标（受害者浏览器不由 Worker 提供），并进行独立玩家全链验收；
- 要么把这台标记为**浏览器漏洞已确认、完整玩家任务未闭环**，另外选择真正无需管理员就能触发的轻量真实 XSS 应用，制作基础专项。

**不要**因为 Worker 只负责调度，就错误地将无法获取管理员会话的 XSS 题说成“应由 Worker 负责 Bot”，也不要为了“直接返回 Flag”放弃实际漏洞验证。

#### 新题评审检查

每台靶机 PR 都说明：
1. Flag 在**靶机里**如何通过目标漏洞自然可获得（至少有玩家路线）。
2. Web 后端里哪一个阶段保存对应答案；静态 vs 实例级答案是否与现有判题实现匹配。
3. Worker 只负责启动/停止、网络和容器，任何 Flag/Bot/题型特有逻辑都必须在靶机或明确的 Web 业务层中。
4. 外部独立玩家环境完整验证所声明的 Flag 获取路径，而不是从测试员的管理员登录捷径读取。

## SQLi 历史专题目录与原题保留


这是**待复现的原题研究目录**，不是已完成的靶机、可同步挑战或官方 HTB/OffSec 镜像。不得重新发明一个自制漏洞应用，冒充原题复现。

**首个研究对象为 OffSec PG Pebbles**：先读 [原题服务与攻击链复原方案](../labs/pebbles/RECONSTRUCTION.md)，确认上游 ZoneMinder 1.29.0 与 Ubuntu 16.04 的实际版本和服务配置，然后验证 Docker 环境。其他目录只是先前选题，必须先补齐原题技术栈和侦察路径，才能决定是否制作。平台内容同步忽略 README.md。

| 顺序 | 目录 | 主考点 | 参考 |
| --- | --- | --- | --- |
| 1 | [01-credential-gate（原归档 01） | **暂停：先前原创登录应用不符合原题复现要求** | PG Cockpit 原生服务核对后再决策 |
| 2 | [02-union-ledger（原归档 02） | 回显 SQLi、查询结构判断和信息提取 | HTB Union |
| 3 | [03-blind-recovery（原归档 03） | 布尔/时间盲注与状态判断 | HTB Usage |
| 4 | [04-asset-gallery（原归档 04） | SQLi 作为第一道关口，上传解析作为第二关口 | HTB Magic |
| 5 | [05-source-trail（原归档 05） | 从实际查询逻辑定位注入并确认数据库权限 | PG Hawat |
| 6 | [06-socket-ledger（原归档 06） | 初始突破之后才出现的 WebSocket 注入入口 | HTB Soccer |
| 7 | [07-monitor-console（原归档 07） | 服务信息、管理 API 与真实产品 SQLi 的组合 | HTB Monitored |
| 8 | [08-camera-database（原归档 08） | **当前优先：真实 ZoneMinder 1.29.0、隐藏 /zm、MySQL 文件写入和 UDF** | PG Pebbles |

#### 当前平台约束（已核对仓库）

- **当前只上线 Linux Docker 靶机。** 暂不纳入 Windows、Active Directory、MSSQL Windows 专属链、内核提权或容器逃逸题目。
- 目录分工：`challenges/<category>/<slug>/` 存学员题面及 Writeup，`labs/<slug>/` 存 Dockerfile、启动脚本、真实服务、测试与素材。不要在规划目录中添加 Dockerfile 触发镜像构建。
- Docker 镜像由 `.github/workflows/lab-images.yml` 根据 `labs/**/Dockerfile` 构建，采用 Linux/amd64；运行实例由平台 Worker 管理。**一题一镜像、一实例一容器**为目前最稳妥的默认设计。确实需要多服务时可在同一容器内运行真实进程，使用内部回环端口和独立账户；不预设平台支持 Compose 多容器编排。
- 优先选择 PHP、Python、Node.js、Ruby、Java、SQLite/MySQL/PostgreSQL、FTP/SMTP/SNMP/Redis 等在 Linux 容器里可复现的场景。涉及 systemd、SUID、Capabilities、sudo 时，必须先在平台真实容器权限配置下做端到端验证；不能为复现强行放开宿主机权限。
- **现阶段使用静态 Flag**，遵循当前 `attackbox/docs/content-authoring.md` 中的 `quiz.answer` 判题机制。用户、Root 是否双 Flag 取决于原题真实利用链，不增加不必要的阶段。

#### 统一要求

- 每题必须指定**唯一的主考点**、首次可见入口、关键转折和预期获胜条件。
- 真实软件漏洞须固定确切的受影响版本并在隔离环境实测；不能以伪造接口冒充 CVE。
- 同一专题中不同机器应有明显的技术差异，而不只是换网页风格或参数名。
- 正式题目提交前：**真实来源/版本/前端与服务端口复原**、构建脚本、健康检查、静态 Flag、重置测试、完整 Writeup 与许可检查均需过关。
- 单独 Web 挑战不强制 Root；完整 Linux 机器的低权限与 Root 阶段必须真实隔离。
- 不将未验证环境、正式 Flag、真实凭据、未授权原题素材直接发布到公开仓库。开发期可使用明确标识的演示 Flag，但发布时必须有正确的私密初始化流程。

参考内容编写规范：`attackbox/docs/content-authoring.md`（另一个仓库）；本仓库已有 `challenges/startpoint/` 与 `labs/` 结构可作样例。


## 2026-11-25 — Historical SQLi composite candidate: HTB Intense

**Selected for implementation:** [HTB Intense](https://www.hackthebox.com/machines/intense). The current inventory already contains UNION, Boolean/Time Blind, second-order, database FILE operations and WebSocket blind SQLi. Intense adds a distinct SQLite conditional-error oracle, followed by a cryptographic session-forgery step and authenticated path traversal.

### Public source review

The Web attack path was cross-checked against multiple independent writeups:

- https://romanh.de/writeup/htb-intense
- https://www.willsroot.io/2020/11/intense-hackthebox-writeup.html
- https://github.com/zweilosec/htb-writeups/blob/master/linux-machines/hard/intense-write-up.md

The common observable sequence is: guest login → public Flask source archive → 140-character message form → SQLite INSERT injection with native error feedback → extract the administrator's stored secret using a conditional error oracle → exploit the custom SHA-256 secret-prefix LWT signature with a length-extension attack → duplicate session keys make the appended administrator identity take precedence → admin log view/list → path traversal to read the Web Flag.

### Reconstruction boundary

The original private application source is not copied. Rebuild the observable route and exploit path with a small independently written Flask application and a real SQLite database. Preserve the normal guest workflow, source archive, message length and filter behavior, direct SQLite errors, conditional error distinction, weak LWT MAC, duplicate-key parsing and unchecked log path join.

The target does **not** include the original SNMP command execution, SSH pivot, custom native note-server binary or Linux Root stages. Those are outside the current Web-only objective. A single final Web Flag is sufficient; do not create a Flag for every intermediate technique.

### Difficulty and engineering

- **Trytopwn difficulty:** Advanced. The Web portion combines SQLi, character-by-character extraction, hash length extension, session parsing behavior and authenticated file traversal.
- **Runtime:** Python / Flask + embedded SQLite. No separate database service, JVM, SSH, SNMP, compiler or privileged capability.
- **Container:** Multi-stage Alpine build, unprivileged web process, per-instance flag file injected at startup, healthcheck, no host mounts or added capabilities.
- **Verification:** CI is limited to build, startup, healthcheck and ordinary page smoke checks. The SQLi oracle, secret extraction, forged session and final file read remain separate manual acceptance tasks.
- **Current status:** implementation branch created; Docker build, measured image/resource usage, manual acceptance and Worker integration are still pending.

The structured machine entry and rolling backlog are maintained in [web-curriculum.json](../catalog/web-curriculum.json).
