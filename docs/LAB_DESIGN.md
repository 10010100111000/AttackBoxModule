# trytopwn 靶机设计与交付规范

> **唯一设计文档入口 · v1 · 2026-11-24**
>
> 适用：AttackBoxModule 所有 **Web 渗透测试与 Linux Docker 综合靶机**。本文件统一替代原有的知识分类、选题评审、路线图、Docker 范围、Flag 职责边界及 SQLi 规划说明。靶机内部 README 只记录该靶机的具体复现和测试，不再复制全局规则。
>
> **权威数据源（不是另一套说明文档）**：[技能目录](../catalog/web-competencies.json) · [机器、候选与开发队列](../catalog/web-curriculum.json) · [CI 工作流](../.github/workflows/)。
>
> 本页的清单属于 **main 分支快照**；任何未合并 PR、当前 GitHub Actions、生产 Worker 的状态必须分别核对，不可仅凭本文判定可发布。

## 1. 设计目标与边界

trytopwn 通过真实的 Web 安全漏洞和必要的 Linux 运行环境，让玩家完成**侦察 → 发现 → 理解 → 利用 → 取证/Flag**。同一个知识点可以重复出现，不设“SQLi 只能三台”或“题库九台封顶”。重复必须有实质差异：请求输入、数据库方言、回显/盲注机制、限制条件、侦察路径、跨服务边界、目标权限中至少一项，并在 CI 中证明。

**当前支持：** Linux/amd64、一个玩家实例对应一个 Docker 目标镜像/容器；Web 专项可单 Flag，综合机器可有 User/Root 两个阶段（由真实链决定）。按现有 Worker 能力，不假定一题支持 Compose 多容器编排。多项真实服务若必须共存，须在同一目标容器内分别运行与监控。学员的 AttackBox 金盘/Btrfs/Namespaces 与 Docker 靶机是两条独立的运行体系。

**当前排除：** Windows/AD、需 Windows 主机的 MSSQL/IIS、Docker/宿主机容器逃逸、模拟 CVE/伪造漏洞、要求 `--privileged` 或挂载宿主 Docker socket/根目录才能完成的题目。真实产品源代码不公开时，必须明确区分“原版组件漏洞”与“根据公开行为重建的界面/流程”，不得宣称官方镜像或源码一比一复刻。

**网络安全：** 有漏洞的服务只在每个玩家独立的私有练习网络里运行；不得把服务直接暴露公网、共享宿主机网络或让实例访问平台管理面。例外能力如 `NET_ADMIN`、SUID、`sudo`、浏览器 `--no-sandbox` 均须写出理由、最小权限与真实 Worker 验收结果，不能把 CI 通过当作宿主安全证明。

## 2. 仓库入口与文件职责

| 位置 | 唯一职责 | 不应放什么 |
| --- | --- | --- |
| **本文件 `docs/LAB_DESIGN.md`** | 全局设计、分类、选题、制作与交付规范、当前关注点 | 重复维护完整机器状态表 |
| `catalog/web-competencies.json` | 31 个 Web 专题、219 个细分技能 ID、首次训练难度、专项验收标准 | CI 运行日志长文 |
| `catalog/web-curriculum.json` | 机器及状态、候选来源、开发 backlog、场景变体及 CI 证据链接 | 每台机器的 Docker 启动细节 |
| `labs/<slug>/` | Dockerfile、启动/健康脚本、真实脆弱服务、Flag 初始化、独立攻击测试、该题 README | 全站分类路线图或通用教程 |
| `challenges/<category>/<slug>/<title>.md` | 平台向玩家显示的正式中文题面、阶段任务与 Quiz | 答案泄漏、通用架构决策 |
| `challenges/<category>/README.md` | 可选的专题导览/历史选题笔记，须链接本文件；不能被当成机器状态主数据 | 复制粘贴的八份“设计占位” |
| `.github/workflows/` | 每题 CI、共享校验及 GHCR 发布门禁 | CI 之外人工声明“已测试” |

**以后修改进度只更新 JSON 主清单和对应 PR/CI，不在多份 Markdown 各写一个“当前第 N 台”。** 新增技能改 competencies；新增靶机、候选、计划和实测证据改 curriculum。机器 README 是技术事实的最细粒度记录；它与 JSON 冲突时查 GitHub 实际代码、CI 和 Worker 证据，不根据文档猜测。

## 3. 知识结构、范围与难度

结构为：**topic → skill → variant → lab → acceptance evidence**。

- `topic_id`：主专题，例如 `sqli`、`xss`、`ssrf`、`file_read`、`command_injection`、`auth_session`、`file_upload`、`nosql`。
- `skill_id`：可独立证明的具体技能，例如 `sqli.boolean-blind`、`sqli.second-order`、`xss.reflected`。
- `variant_id`：同一技能的场景差异，例如 Cookie + MySQL + 无报错；WebSocket + JSON 消息 + 布尔反馈。不是换标题、颜色或 Flag。
- `lab`：对应一个可独立运行的真实环境，一个主技能、若干次技能。
- `evidence`：独立攻击者、实际数据库/浏览器/协议栈执行与重置的可复核 CI 日志。

专题按 PortSwigger Web Security Academy 的公开课程结构划为 **14 个服务端、6 个客户端、11 个进阶**，完整技能表以 JSON 为准。服务端包括 SQLi、认证、遍历、命令注入、业务逻辑、信息泄露、授权、上传、竞态、SSRF、XXE、NoSQL、API、缓存欺骗；客户端包括 XSS、CSRF、CORS、点击劫持、DOM、WebSockets；进阶包括反序列化、LLM、GraphQL、SSTI、缓存投毒、Host header、走私、OAuth、JWT、原型污染与基础技能。并非每台机器必须覆盖多个漏洞。

| 难度 | 玩家路径设计 | 不能用作唯一依据 |
| --- | --- | --- |
| **初级** | 自然可发现的入口，单一主要机制，基本枚举与请求观察 | 只有一个 Flag、隐藏目录少 |
| **中级** | 多页面/角色、不同回显或输入上下文、盲注、简单凭据/权限转移 | 漏洞编号很旧、机械增加步骤 |
| **高级** | 多协议、带外、真实浏览器策略、缓存/解析器/竞态边界或多个独立约束 | 只调低成功率、加深目录、增大镜像 |

技能的 `first_target_level` 是**首次练习的建议难度**，不限制同一机制在更高难度重新出现。专项可只取得业务证明或单 Flag；系统综合题的 User/Root 必须由真实身份/权限界限分离，不能凭空添加提权环节。

## 4. 从真实原题到正式候选：评审门槛

### 4.1 来源优先级

优先检索原版开源受影响组件、官方安全公告、确定的脆弱/修复版本及公开历史 Writeup。HTB/OffSec 的私有前端、脚本或二进制若未授权获取，只能**如实注明重建的可观察行为**；真实漏洞应尽量落在可核验的原始软件/依赖版本。不能制造易注入接口再给它贴 CVE 标签。

对每个候选，至少记录：

1. **source**：HTB/OffSec/上游软件/Writeup URL，许可及哪些素材真实可用。
2. **upstream**：原始服务、Web 前端、数据库/框架、确切受影响版本、补丁差异、触发代码与前置条件。
3. **route**：首屏与端口 → 侦察/枚举 → 输入点 → 真漏洞 → 获取能力 → Flag；玩家不能一开始看到答案提示。
4. **knowledge**：topic、主/次 skill、variant、难度和相对于已完成机器的学习增量。
5. **container**：必要进程、端口、数据库、依赖、预计镜像与 RAM、用户与能力、Worker 兼容性。
6. **acceptance**：外部独立攻击者如何证明真漏洞、同版本修复对照、原生权限、Flag、实例重置与隔离。
7. **risk/decision**：未知源代码、版本不可得、特殊宿主权限、单容器多服务风险；明确下一状态。

### 4.2 量化评审（100 分）

| 维度 | 权重 |
| --- | ---: |
| 原始证据、组件真实性 | 25 |
| 相比已有题的技能增量 | 20 |
| 自然的侦察、枚举与发现链 | 20 |
| 可重放的独立黑盒验收 | 15 |
| Linux Docker/Worker 可移植性与安全 | 15 |
| 构建体积、运行资源与可维护性 | 5 |

建议 **≥75 分** 再实施。**无论分数多高，一票否决**：假漏洞/假提权、缺失必要源代码而隐瞒、以宿主机逃逸为目标、必须开特权容器或开放平台管理面、唯一利用链无法在隔离环境中复现。

## 5. 单台靶机的完整设计模板

每台机器的 `labs/<slug>/README.md` 应按如下顺序撰写实际内容，禁止只填通用占位话术：

1. **基本信息**：标题、slug、主/次技能、variant、初/中/高级、专项/综合、上游来源及 license。
2. **原题与证据**：官方/第三方原始材料、受影响版本/修复版、关键真实代码或配置、哪些页面是行为重建。
3. **侦察路径**：开放端口、首屏、普通业务、可发现信息、枚举后的隐藏服务、误导线索；不把漏洞参数写在首页。
4. **攻击链与权限图**：每一步的请求/服务、输入条件、普通用户与管理员权限、用户/Root 或业务目标。分清「真实 CVE」「开发者有意不安全的业务查询」「原版已知漏洞」。
5. **Flag 目标**：谁可以读、漏洞为什么能抵达该目标、Flag 在何处生成或保存、Web 如何判题、重置后怎样失效；不允许根据 payload 字符串匹配直接发 Flag。
6. **单镜像运行架构**：Dockerfile 基础镜像与锁定版本、非 root 进程、数据库/浏览器/SSH 是否必要、端口、文件系统、健康检查、启动/停止/清理、日志及失败行为。
7. **镜像优化**：多阶段构建与清理包缓存/编译依赖；删除无关服务但不能删掉真实利用前置条件。报告 `docker image inspect .Size` 实测字节、内存/PID 快照；不要凭软件包大小推断镜像大小。
8. **独立 CI 与修复对照**：攻击者容器独立于目标容器，不读目标秘密；必须覆盖浏览/枚举 → 真漏洞 → Flag，失败时保留足够日志，校验修复版不再被利用。
9. **发布差异**：原版哪些服务被省略、哪些仅模拟外观（不模拟漏洞）、与真实 Worker 哪些能力尚未验证、哪些安全限制/发布门禁未通过。

**目录样式：**

```text
labs/<slug>/
  Dockerfile
  .dockerignore
  README.md
  scripts/           # 真实初始化与进程监管、健康检查
  site/              # 可合法使用的原版软件及必要业务包装
  tests/             # 独立攻击者、非特权黑盒验收
  .release-blocked   # 仍有发布缺口时保留

challenges/<category>/<slug>/
  <title>.md          # 只有正式可同步的题面
```

真实上游源码可以通过锁定版本的构建流程下载/验证，未必需要直接提交整个源码树。不要为了符合目录结构创建没有内容的空文件夹。

## 6. 平台、Worker、容器与 Flag 的职责

| 组件 | 负责 | 不负责 |
| --- | --- | --- |
| **Web 后端** | 题目/阶段正确答案、提交与判题、完成状态；若将来启用动态 Flag，负责正确答案与实例的关联 | 模拟漏洞利用或管理员浏览器 |
| **Worker** | 镜像分发、启动/停止、网络、资源限制、实例生命周期、传递不透明运行参数 | Flag 判题、生成题目漏洞、XSS Bot、自动审阅 |
| **靶机容器** | 原版漏洞服务、目标权限/文件/Flag、题目需要的管理员 Bot 与业务流程、实例初始化 | 判断玩家向平台提交的答案是否正确 |

**Flag 分类**：
- **当前能确认的兼容方式**：Web 后端存固定阶段正确答案；靶机容器中按题目配置放置相同 Flag，CI 的 demo 值不能作为生产答案。把环境变量传给容器并不代表 Worker 负责 Flag 业务。
- **实例级动态 Flag**：只有当 Web 后端的阶段答案与实例 ID、启动代次、重置/停止失效逻辑真正对齐时才能标记“上线支持轮换”。靶机端可以随机生成/注入 Flag，但若 Web 仍只比较静态答案，就只能称「靶机实例侧轮换」，不能声称平台完成动态判题。
- **User/Root**：仅在原题有真正不同的访问权限时分两枚。Web 专项允许单 Flag；管理员信息应由管理员会话/真实权限操作才能取得。
- **XSS Bot**：基础 XSS 不要求 Bot；管理员会话或 Blind XSS 的目标则必须有真实浏览器受害者访问流程。Bot 属于目标容器内部，可使用无头浏览器；不能由 Worker 代劳。不能直接返回 Flag 或检查脚本关键字假装 XSS 已执行。
- **进程隔离**：若浏览器必须使用 `--no-sandbox`，明确记录额外风险；无论如何禁止 `--privileged`、宿主挂载、Docker socket，优先在真实平台验证可用的更严格沙箱方案。

## 7. CI、发布与状态词的严格定义

```text
研究候选 → 来源/版本核验 → 设计评审 → 实际构建
    → 原生漏洞验证 → 独立完整攻击链 CI → Worker 实机验证 → 发布
```

| 状态/字段 | 必须有的实际证据 |
| --- | --- |
| `researching`、`source_verified` | 官方/上游/Writeup 与具体版本；没有完成代码承诺 |
| `implemented` / `in_progress` | Dockerfile、真实组件、启动脚本等代码可查；不代表构建或利用成功 |
| `lab_ci_status=unverified` | 缺少独立验证 |
| `lab_ci_status=partial` | 只通过启动、服务、单一漏洞或部分 Flag 阶段 |
| `lab_ci_status=full_chain_ci` | CI 中独立普通玩家完成真实攻击链并拿到目标 Flag；记录运行 URL/commit |
| `worker_status=verified` | 真实 Worker 按实际网络/CPU/RAM/PID/权限配置运行，多实例隔离、重置、流量入口验收 |
| **可发布** | lab + Worker 通过、Web 判题匹配、合法素材与必要的发布门禁清除 |

CI 至少检查：构建（真实镜像字节数）、健康与端口、侦察入口、真实组件/漏洞版本、从外部取得 Flag、非授权访问拒绝、修复对照（可行时）、实例销毁重建/旧状态清理、资源快照、限制能力和错误日志。真正无法测试的环节须保留 `.release-blocked`，并在 PR 中写明原因。

**必须做到“设计好靶机 + 完整 CI 通过，再向用户报告完成”。** 完成 README、Dockerfile 或仅 HTTP 200 不等于完成；GitHub CI 红灯要读取日志修复、重新验证。不得说“以后再测试”而把题目计入完成。

## 8. 全题库的滚动方向与 SQLi 专项计划

**状态真值只在** `catalog/web-curriculum.json`；此节是选题逻辑，不重复静态台数与会过时的“下一台已完成”文字。

### 8.1 SQL 注入：15 个技能目标

SQLi 以 [PortSwigger SQL injection](https://portswigger.net/web-security/sql-injection) 为分类参照。15 个技能为：

| 训练阶段 | 主机制/技能 ID | 训练重点 |
| --- | --- | --- |
| 基础 | `sqli.auth-bypass`、`sqli.where-hidden` | 查询逻辑/隐藏数据 |
| 回显 | `sqli.union`、`sqli.union-column-count`、`sqli.union-type`、`sqli.db-enumeration` | 列数、类型、真实数据枚举 |
| 异常 | `sqli.error-based`、`sqli.conditional-error` | 原生数据库报错与条件错误 |
| 无回显 | `sqli.boolean-blind`、`sqli.time-blind` | 真/假差异、真实 DB 延时、可重复提取 |
| 状态/能力 | `sqli.second-order`、`sqli.file-operations` | 写入后的消费点、数据库 OS 权限 |
| 进阶 | `sqli.oast`、`sqli.filter-bypass`、`sqli.stacked-query` | 带外、编码与语法差异、多语句 |

**现有对应机器**：Union（UNION、文件读取）、Validation（二阶 SQLi、文件写入）、Pebbles（原版 ZoneMinder 1.29.0 SQLi、MySQL 文件/UDF）、GoodGames（登录 SQLi，主清单标记部分验收）。这些是有价值但不同的场景；不得因此把未验证的布尔/时间盲注标为覆盖。

**历史研究候选的归并清单**（继承原 `challenges/sql-injection/01…08` 占位 README，状态以主清单/CI 为准）：

| 候选 | 目标和起始路径 | 处理 |
| --- | --- | --- |
| PG Cockpit | 真实 blaze PHP/MySQL 登录 → Cockpit 9090 → Authchecker 权限问题 | **暂停**：原版 Blaze 私有前端与 Authchecker ELF 的许可/源码不可核实，不再用自编登录页伪装原题 |
| HTB Union | 原始风格资格查询 → UNION → 数据/SSH/后续执行 | **已有 `labs/union`**，见该目录 CI；原候选 README 已过时 |
| HTB Usage | 账户恢复 API → 无回显 SQLi → 后台访问 | **优先研究**：布尔/时间具体机制必须先核对 Writeup，不凭候选标题断言 |
| HTB Magic | 登录 SQLi → 原生上传处理 → Foothold | 候选，需核对真实组件与后续权限链 |
| PG Hawat | 源码/配置发现 → SQL 查询与文件权限 | 候选，需核对原版证据 |
| HTB Soccer | 实际 WebSocket 消息 → 布尔盲注 → SSH/后续权限 | **高价值候选**，需真实 WS 服务/SQL DB 而非 HTTP 换皮 |
| HTB Monitored | SNMP/管理 API → 产品 SQLi → 管理权限 | 候选，高资源复杂度，先调查原版 Nagios 组件 |
| PG Pebbles | 端口/路径枚举 → **原版 ZoneMinder `/zm/`** → 真 SQLi → DB `INTO OUTFILE` → UDF | **已有 `labs/pebbles`**，原版漏洞与核心链已有 CI，Worker 尚需验收 |

**后续 SQLi 优先**：① 修补现有 GoodGames 部分链与单容器适配；② 布尔盲注（Cookie/隐藏 API/真实 DB 差分）；③ 时间盲注（多次采样及噪声控制）；④ HTB Soccer 风格真 WebSocket 盲注；⑤ 报错型/条件报错、OAST、另一数据库方言。候选定级与排序可以随上游证据和 CI 可行性改变。

### 8.2 XSS 与其他专题

XSS 必须区分 HTML 正文、属性、JavaScript 字符串、URL、DOM source/sink、存储型、Blind/管理员浏览器、CSP 与跨用户权限操作；必须由**真实浏览器执行证据**支持。WonderCMS 和 Django 的新开发 PR 不应被旧 main 快照的“XSS 都没完成”文字覆盖，须查询对应 PR 的实际 CI 与发布门禁。

其余 29 个专题在 competencies JSON 中都存在独立学习目标。滚动补齐优先级示例：认证/访问控制、LFI/遍历、NoSQL、CSRF/CORS、真实文件上传、SSRF、XXE、反序列化、JWT/OAuth、GraphQL、缓存与请求走私等。选题看**缺少的技能 + 场景增量 + 原版源码可得性 + Worker 可复现性**，而不是一次性设定题目配额。

## 9. 维护规则与日常开发步骤

1. **从本文件开始**，读取 `catalog/web-competencies.json` 与 `catalog/web-curriculum.json`；检查现有 `labs/`、已合并 PR、开放 PR 与相关 CI。
2. 选择缺口 skill + variant，核实原题、上游、Writeup、版本、许可与完整利用路径；使用 §4 评审。
3. 每台靶机创建独立开发分支与 Draft PR；本 PR 内完成真实 Dockerfile、启动、服务、Flag、健康、独立攻击测试和专项 GitHub Actions。
4. 根据实际 CI 修复，直到真实玩家链通过；记录镜像大小/内存/进程/限制、重置、修复对照。
5. 更新 **唯一主清单**的状态、CI 链接及 variant，机器 README 保留技术证据；保留 `.release-blocked` 直到 Worker/判题/发布校验实际通过。
6. 报告明确区分「已设计」「已构建」「CI 全链通过」「Worker 已验收」「正式发布」，无证据不升级状态。
7. 修改全局政策只编辑**本文件**；不要再新建另一个 WEB_ROADMAP、SQLI_PLAN 或 FLAG_RULES 复制同一内容。知识目录与状态数据只更新各自 JSON。

### 原始项目参考

- PortSwigger Web Security Academy: https://portswigger.net/web-security/all-topics
- HTB machines: https://www.hackthebox.com/machines
- Vulhub: https://github.com/vulhub/vulhub
- PG Pebbles 的可复核实物资料：[`labs/pebbles/RECONSTRUCTION.md`](../labs/pebbles/RECONSTRUCTION.md)
- 真实 Worker 最终契约：`10010100111000/attackbox` 中的 `worker/node/targets/`、`web/server/services/challenges.ts` 与题库配置；不要把此处的历史说明当作当前代码替代品。
