# Web 靶机选题与复现评审规则

版本：2026-11-23 / v2。**本文件解决“知道缺哪个知识点，但不知道该选哪台机器”的问题。**

配套：
- [31 个官方专题、219 个自编知识目标](../catalog/web-competencies.json)
- [现有 17 台机器及选题队列](../catalog/web-curriculum.json)
- [知识点与三级难度](WEB_TAXONOMY.md)
- [滚动路线图](WEB_ROADMAP.md)

## 1. 不排除重复：只排除“没有增量的重复”

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
5. **能否工程化**：Docker Linux 私网可运行、小镜像、健康检查、隔离、实例重置、独立 CI、Worker 兼容。

同一个 `skill_id` 的第二台机器应具有 `variant_id` 和上述差异说明；同一技能可以有多个 `variant_id`，绝不设“一个点最多一题”或“每类最多三台”。

## 2. “专项”与“综合”分别挑选

| 类型 | 选题标准 | 可接受的目标 |
| --- | --- | --- |
| Web 知识专项 | 一种细分机制讲清楚；真实浏览器/数据库/协议栈，可从普通页面自然发现 | 单 Flag、业务状态改变、权限获取或可观测证据，不强制添加系统 Root |
| Web 综合靶机 | 原始侦察 → 真实 Web 漏洞 → 凭据/移动 → SSH/User → 原生 Linux 权限提升/Root | 依据原题是否双 Flag，避免凭空增加提权链 |
| 复合题 | 例如 SQLi + LFI、XSS + CSRF、SSRF + 内部 API；先明确**主要技能**，剩余标为次要技能 | 每一环有独立证明；难度按整个玩家路径定，不按漏洞个数定 |

### 重复如何判定：以 SQLi 为例

| 机器/场景 | 可以同时存在吗 | 不同的知识目标 |
| --- | --- | --- |
| Union（已有） | 可以 | MySQL/PHP UNION + FILE + HTTP header/SSH |
| Validation（已有） | 可以 | 二阶注入：先存储参数，再由另一请求消费 |
| Pebbles（已有） | 可以 | 真实 ZoneMinder，SQLi → 数据库文件与 UDF 影响 |
| 另一台 Cookie 布尔盲注 | **应该加入** | 没有直接回显，需要比较响应推断数据 |
| 另一台 PostgreSQL 时间盲注 | **应该加入** | 不同数据库语法、延时噪声与统计 |
| Soccer（候选） | **应该加入** | WebSocket 帧传输、盲 SQLi 与跨协议链 |
| 又一台普通 PHP UNION 登录 | 可以，但**低于前述优先级** | 只有在输入环境、数据库或约束不同、确有教学增量时才选 |

### XSS 不能只看“弹窗”

至少分别覆盖：HTML 正文、HTML 属性、JavaScript 字符串、DOM source/sink、存储型、管理员浏览器 Blind XSS、CSP 真正生效下的限制、浏览器内执行导致权限操作。**这些可以由多台机器重复交叉练习。**

## 3. 候选机器评审表（100 分）

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

### 评审时必须写的 `candidate_review`

- `source`：HTB/OffSec 原题 URL、Writeup、公开代码 URL；是否原版源码？
- `upstream`：软件/依赖/协议的具体受影响版本；补丁前后的差异。
- `route`：侦察 → 漏洞 → 获取能力 → 目标 Flag 的完整玩家路径。
- `knowledge`：主 `skill_id`、次要 `skill_id`、难度、先修技能。
- `variant`：和现有机器相比具体新增什么；输入面/反馈/约束/栈至少一项有意义的不同。
- `container`：真实需要的服务、典型 RAM/镜像目标、端口、capability、禁止 host 权限的实现。
- `acceptance`：独立容器看到的 HTTP/浏览器/协议证据、真实 UID、Flag 与重置。
- `risk`：未公开的源代码需要重建哪些可观察行为？哪些细节尚未证实？
- `decision`：`researching` → `source_verified` → `feasible` → `in_progress` → `lab_ci_verified` → `worker_verified`。

## 4. 已有公开证据的真实机器候选（不是制作承诺）

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

## 5. 实际制作顺序：持续滚动，不以“9 台完成”为终点

1. 先检查 [细分知识目录](../catalog/web-competencies.json) 中尚无独立测试的目标，并确定场景变体；**优先补薄弱基础，但不限制重复数量**。
2. 对比上表的公开候选，选择最容易核实真实技术、侦察真实且 Docker 可行的一台；必要时对同一知识点选多台不同复杂度。
3. 只为选中的机器创建开发 PR；更新 [主清单](../catalog/web-curriculum.json) 的 `backlog`，在 PR 中放入 `candidate_review`。
4. 先通过靶机专属的外部入口 → 利用 → 目标 Flag/权限 CI；记录运行镜像字节数、内存、隔离和重置。
5. 再单独通过正式 Worker 的网络、权限、动态 Flag 判题与多用户资源验收。两个层次不混淆。

**选题优先级 = 缺少的知识训练价值 + 与已有靶机的有意义差异 + 真实可复现性，不是“这个漏洞已有 1 台所以禁止再选”。**
