# trytopwn Web 题库知识点与难度标准（v2）

**更新：2026-11-23。以 PortSwigger Web Security Academy 的公开专题结构为参考，但知识点、变体场景及难度规则均为 trytopwn 独立编写；不复制官方练习。**

## 一、为什么不能用“每类至少三台”规划题库

以前的规划很容易变成 SQLi 三台、XSS 三台，完成数量后便停止。同一类别内部包含彼此完全不同的攻击机制；即使相同机制，也可能在输入面、回显方式、限制条件和数据库语法上存在值得反复训练的变体。

**新的基础结构：`专题（topic） → 细分知识点（skill） → 场景变体（variant） → 真实靶机（lab） → 独立验收证据（evidence）`。**

- **专题数不等于覆盖率**：某台机器含 SQLi，只说明它涉及 SQLi，不代表盲注、报错、OAST 都覆盖。
- **知识点不限制重复次数**：同一 `skill_id` 可以关联多台真实机器，每个场景记录 `variant_id` 与明确的教学增量。
- **现有标签不自动成为细分技能已验证**：目前旧机器清单的 `validated_skills` 是历史 CI 关联证据，具体技能还需对应单独断言。新技能表默认 `not_audited`，避免虚报。
- **难度属于整道题的玩家体验**：每条知识点的 `first_target_level` 只是适合第一次练习的深度，技术可以重复出现在更高等级。
- **一台机器有一个主专题、若干次要知识点**；统计专题覆盖只按主标签，统计技能训练按真实有证据的场景变体。

参考：[PortSwigger 官方 31 专题](https://portswigger.net/web-security/all-topics)、[所有学习资料](https://portswigger.net/web-security/all-materials)、[选题评审与真实机器候选](WEB_MACHINE_SELECTION.md)。完整结构化目录：[**219 个目标**](../catalog/web-competencies.json)。

## 二、按照官方专题逐一编入题库

这里列出 **31 个专题**（14 服务端、6 客户端、11 进阶），每个专题已分解成可以独立验收的具体目标。表中的数字是**规划中的知识目标数量**，不是已完成的靶机数量。

### 服务端专题 (14)

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

### 客户端专题 (6)

| 专题 | 知识目标 | 例：从基础到进阶 |
| --- | ---: | --- |
| [Cross-site scripting (XSS)](https://portswigger.net/web-security/cross-site-scripting) (`xss`) | 12 | 基础反射型 XSS → DOM sources 与 sinks → 由浏览器脚本完成跨用户权限操作 |
| [Cross-site request forgery (CSRF)](https://portswigger.net/web-security/csrf) (`csrf`) | 8 | 无防护状态修改请求 → SameSite 规则和跨站请求差异 → XSS 与 CSRF 跨上下文组合 |
| [Cross-origin resource sharing (CORS)](https://portswigger.net/web-security/cors) (`cors`) | 5 | 任意 Origin 回显和敏感数据暴露 → 误信可控制的子域来源 → 动态 CORS 头与缓存相互影响 |
| [Clickjacking](https://portswigger.net/web-security/clickjacking) (`clickjacking`) | 4 | 无 X-Frame-Options/frame-ancestors 的嵌入 → 多步骤 Clickjacking → Clickjacking 与状态更改组合 |
| [DOM-based vulnerabilities](https://portswigger.net/web-security/dom-based) (`dom_vulnerabilities`) | 8 | DOM 输入来源与危险 sink 的识别 → DOM-based cookie 操作 → 浏览器模板动态执行 |
| [WebSockets](https://portswigger.net/web-security/websockets) (`websockets`) | 5 | WS 连接、协议与消息结构探测 → WS 消息渲染注入 → WebSocket 承载的盲注或跨协议数据提取 |

### 进阶专题专题 (11)

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

## 三、SQL 注入：按机制而不是“注入题数量”统计

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

## 四、XSS：必须区分浏览器上下文

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

## 五、SSRF 与路径遍历：同一个名称仍可有多种深入情景

| 知识模块 | 基础训练 | 中级变体 | 高级变体 |
| --- | --- | --- | --- |
| SSRF | 本机回环 API、真实服务器端请求 | 内网端口枚举、重定向、黑名单 | URL 解析器差异、OAST、跨服务链 |
| 路径遍历 / LFI | 文件读取与相对路径 | 绝对路径、嵌套剥离、双重解码、前缀/后缀限制 | LFI 包装器、文件到 RCE 的多阶段链 |

Editorial 已对 SSRF 基本与内网 API 访问做了完整攻击链 CI，但**不代表** URL 校验绕过、Blind SSRF 或多协议组合已完成。Trick 与 Inject 是不同 LFI/路径遍历综合链的候选，必须经过真实源码/Writeup 评审才进入开发。

## 六、初级、中级、高级：难度用什么判定

| 级别 | 真实玩家面对的场景 | 不是判定依据 |
| --- | --- | --- |
| **初级** | 单一机制、清楚但不直白的线索，基础枚举与请求调试，能从正常应用自然发现入口 | 不是因为只存在一个 Flag，也不是非要无认证 |
| **中级** | 多页面或角色、不同数据/回显上下文、盲注/安全限制、简单凭据转移与系统权限 | 不是仅因某个 CVE 在年份较旧或需要 SSH |
| **高级** | 多协议、盲/OAST 反馈、真实浏览器安全策略、解析器/缓存/竞态边界、多个独立限制的组合 | 不是单纯增加密码、把目录名藏得更深或增大镜像 |

高级专题组中的 JWT、OAuth 或 Request Smuggling 也有适合初学者的底层概念；**`first_target_level` 是该细分目标首次训练的建议级别，并不限制后续复练难度。**

## 七、覆盖状态：专题 → 技能 → 场景 → 实际验收

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

### 绝不能混淆的状态

1. `cataloged`：专题/技能已列入计划。
2. `researching`：已找到候选 HTB/OffSec/开源应用，但原始行为、版本和完整链未核实。
3. `implemented`：真实源码和配置已提交，未完整验收。
4. `lab_ci_verified`：独立攻击端完成规定的真实目标链和重置，附 CI/人工证据。**不会因为某台综合机器的 CI 通过就自动让每个关联技能通过。**
5. `worker_verified`：真实平台 Worker 的镜像启动、私有网络、资源隔离和多用户调度通过；**Worker 不判题、不管理 Flag、不提供 XSS 管理员 Bot**。Flag 由靶机经真实利用提供，答案由 Web 后端 `attemptChallenge()` 校验。详见 [平台与 Flag 责任边界](PLATFORM_FLAG_BOUNDARIES.md)。

## 八、如何维护

- 下一台靶机先读 [选题方法](WEB_MACHINE_SELECTION.md)，确认 `topic_id` + `skill_id` + 有意义的 `variant_id`，**允许同一知识点再做很多次**。
- 所有新类别、技能及三个难度入口统一更新 [`web-competencies.json`](../catalog/web-competencies.json)。原 `web-curriculum.json` 保存现有机器、历史 CI 记录与滚动开发队列。
- 保留原始上游代码及版本；没有确切源码时可重建可观察网站行为，但不得将模拟程序伪装成真实漏洞。
- 新的 Web 专项不强制一枚 User + 一枚 Root，综合靶机则要分别验收其原始目标。
- 参考 [仓库路线图](WEB_ROADMAP.md) 的动态优先级，**不再规定只做九台**。
