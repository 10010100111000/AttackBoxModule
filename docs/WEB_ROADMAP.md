# trytopwn Web 题库覆盖盘点与分阶段路线图

**2026-11-23 快照；来源为 GitHub `main`，对照提交 `45c2e88165342dca8ce3583c33659651f5c3c7f2`。** 统计只按唯一主类别计数；各靶机完成状态以代码及可追溯 CI 为准，**不把 main 已合并等同于 Worker 已上线**。请同时阅读 [难度/分类标准](WEB_TAXONOMY.md) 和 [可机读清单](../catalog/web-curriculum.json)。

## 一、库存：17 个目录，16 个 Web（相关）+ 1 个非 Web 服务链

以下“初/中/高”为**暂定难度**，不是玩家实测评级。

| 机器 | 主类别 | 次要知识点 | 暂定难度 | 靶机 CI 状态 |
| --- | --- | --- | --- | --- |
| Base | 认证与会话 | PHP strcmp、上传 | 初级 | 未完整验收 |
| Bashed | 暴露执行入口 | phpbash、sudo、cron | 初级 | 完整目标链 CI |
| Bike | SSTI | Handlebars、服务器命令执行 | 初级 | 局部验证 |
| BountyHunter | XXE | 凭据复用、Python eval 提权 | 中级 | 完整目标链 CI |
| Cap | IDOR | PCAP、FTP/SSH、文件 capability | 中级 | 完整目标链 CI |
| Cursed Stale Policy | XSS / CSP | 浏览器、WebSocket | 高级 | 尚无完整攻击链证据 |
| Devvortex | CMS 组件漏洞 | Joomla、虚拟主机、Apport | 中级 | Root 阶段尚未验收 |
| Editorial | SSRF | 内部 API、Git 历史、GitPython | 中级 | 完整目标链 CI；**Worker 发布封锁** |
| GoodGames | SQLi | Jinja2 SSTI、凭据复用 | 中级 | 部分目标（仅 User Flag） |
| Nibbles | 文件上传 | 真实 CMS 插件、sudo | 初级 | 完整目标链 CI |
| OpenAdmin | 命令注入 | ONA xajax、SSH、nano | 中级 | 完整目标链 CI |
| Pebbles | SQLi | ZoneMinder、数据库文件操作、UDF | 高级 | 有完整链 CI；Worker 待验收 |
| Photobomb | 命令注入 | Sinatra、ImageMagick、PATH | 中级 | 完整目标链 CI |
| Shocker | 命令执行 / Shellshock | Apache CGI、sudo Perl | 初级 | 完整目标链 CI |
| Union | SQLi | MariaDB LOAD_FILE、iptables、SSH | 中级 | 完整目标链 CI |
| Validation | SQLi | 二阶注入、FILE、su | 中级 | 完整目标链 CI |
| Funnel | **非 Web 服务链** | FTP、SSH 转发、PostgreSQL | 初级 | 局部验证；单 Flag |

备注：部分旧 README 仍含“未合并”或早期 Smoke 说明；新目录以 `catalog/web-curriculum.json` 的**快照标签和 CI 证据**为规划基线，验收状态不得反向推断生产发布。`full_chain_ci` 不意味着所有细分技术均已覆盖，例如存在一台 SQLi 综合靶机，并不能自动计为“盲注已覆盖”。

## 二、按漏洞能力而非机器数量衡量覆盖

| 技术大类 | 已有的有效覆盖 | **核心缺口** | 下一轮策略 |
| --- | --- | --- | --- |
| **SQLi** | 登录查询、UNION、二阶、FILE 读写（GoodGames / Union / Validation / Pebbles） | 报错型、布尔盲注、时间盲注、OOB、复杂过滤 | **优先补盲注**，暂不增加普通 UNION 登录靶机 |
| **XSS** | Cursed Stale Policy 存在 CSP/XSS 代码，但完整浏览器攻击链未验收 | 反射型、存储型、DOM、Blind XSS、CSP 验收 | **最大短板：先易后难做三档** |
| **SSRF** | Editorial 的公开封面预览 → 内网 API | URL 校验/重定向绕过、Blind SSRF、复杂服务联动 | 保留 Editorial，新增高级受限 SSRF |
| **IDOR / 授权** | Cap 的数值对象越权 | 多角色越权、多租户隔离、会话/JWT | 后续专项 |
| **文件上传** | Nibbles、Base（Base 验收未全） | MIME/扩展名绕过、解析链、上传竞态 | 中高级专项 |
| **路径遍历／LFI** | 无独立主分类靶机 | 基础遍历、LFI、包装器、文件到执行 | **新增初级** |
| **命令注入** | OpenAdmin、Photobomb、Shocker | 盲执行、参数注入、过滤 | 现阶段暂缓重复 |
| **SSTI** | Bike、GoodGames 的源码路径 | 沙箱限制、完整 CI | 补验收后再扩展 |
| **XXE** | BountyHunter 文件读取 | SSRF / Blind OOB | 中高级补充 |
| **NoSQL 注入** | 无 | MongoDB 操作符、盲提取 | **新增初级** |
| **反序列化** | 仅其他靶机存在 eval 等相关机制，不能当作反序列化专项已覆盖 | 真实不安全反序列化 / 依赖 Gadget | **新增中级** |
| **CSRF / JWT / 业务逻辑** | 暂缺独立专项 | 认证/会话、状态机、竞态 | 第二轮规划 |
| **HTTP 协议** | 有 WebSocket 相关代码但无专项验收 | 请求走私、缓存、WebSocket 盲注 | 高级阶段 |

### SQLi：具体子项

- **已有**：登录/查询注入（GoodGames）、UNION（Union、Validation）、二阶（Validation）、数据库读取/写入文件（Union、Validation、Pebbles）。
- **不足**：报错型盲数据提取、布尔盲注、时间盲注、OOB 与复杂过滤。**复杂的 SQLi 靶机不等于这些子项都存在**。
- **排期**：中级首先补“同一真实数据库上的布尔盲注与时间盲注”，高级再选 OOB/协议组合，不重复做基础 UNION。

### XSS：具体子项

- **反射型**：缺少独立可复现且浏览器实测的基础题。
- **存储型**：缺少真实提交、存储和管理员访问的完整验收。
- **DOM-based**：缺少专项。
- **Blind XSS / CSP**：Cursed Stale Policy 是候选，现阶段只算代码资产，不算“已通过”。
- **排期**：初级反射型 → 中级存储型管理员浏览器 → 高级 Blind XSS/CSP。实际 JavaScript 执行是证据，`alert(1)` 字样、静态字符串回显不是证据。

## 三、第一轮计划：9 个“知识点/难度”需求，不是盲目新开 9 个分支

| 顺序 | 暂定级别 | 主分类与知识目标 | 题型 | 何时算完成 |
| --- | --- | --- | --- | --- |
| **01** | 初级 | **反射型 XSS** | Web 专项 | 真实浏览器执行、上下文验证、提交 Flag |
| **02** | 初级 | **路径遍历 / 文件读取** | Web 专项 | 真实文件接口与授权边界，非硬编码响应 |
| **03** | 初级 | **NoSQL 操作符注入** | Web 专项 | 真 MongoDB/驱动查询、授权绕过和测试 |
| **04** | 中级 | **SQLi：布尔盲注 + 时间盲注** | Web 专项 / 综合 | 实际数据库可重复提取、差异统计 |
| **05** | 中级 | **存储型 XSS + 管理员访问** | Web 专项 / 综合 | 真正的管理员浏览器、会话与权限验证 |
| **06** | 中级 | **真实不安全反序列化** | Web 专项 / 综合 | 受影响版本、原始解析/Gadget、完整链 |
| **07** | 高级 | **Blind XSS + CSP 限制** | 高级 Web | 实际浏览器 Bot、CSP 生效，必要时先验收旧 CSP 靶机 |
| **08** | 高级 | **WebSocket SQL 盲注** | 高级 Web | 真 WebSocket / SQL 数据通道、盲注及限制 |
| **09** | 高级 | **受限 SSRF + 内部服务链** | 高级综合 | 校验器/重定向约束真实生效，连续攻击链可重放 |

> 上表是**能力需求**，不是已经筛选完成的 HTB 机器名单。可考虑 NodeBlog、Trick、Precious、Headless、Soccer 等真实历史案例，但不能未经源码和 Writeup 核查就承诺一定复现，也不能把中级实战伪装成纯初级练习。

### 后续第二轮（暂不并发制作）

补充 DOM XSS、JWT／CSRF、IDOR 多角色、XXE Blind/OOB、文件上传解析差异、业务逻辑/竞态、缓存和请求走私。优先依据第一轮实际覆盖与用户反馈调整。

## 四、挑选机器的具体顺序（每次开新 PR 前先执行）

1. **查缺口**：在上面的覆盖表和 `catalog/web-curriculum.json` 查未覆盖的 `required_skill_coverage`；优先缺口最多的初级档。
2. **查来源**：至少一份可信 Writeup 加官方或上游源码/真实组件；记录原版环境、漏洞编号/版本、页面线索、完整攻击链。无法核实则换候选，不编假服务。
3. **检查 Docker 可行性**：Linux 容器能复现、无需宿主机逃逸或 `--privileged`、不存在不可控的网络依赖；多阶段构建并测最终镜像字节数。
4. **先验收再进度**：一个靶机一个开发 PR，外部独立攻击容器完成侦察 → 漏洞 → 目标权限／Flag，健康检查、跨实例隔离和重置。失败就修，不把 smoke CI 当已完成。
5. **发布分离**：合并代码不代表生产发布。Worker 网络隔离、动态/私有 Flag 判题、限制、负载通过之后才能移除发布阻止标记并手动发行。

## 五、下次继续时如何使用本计划

**默认动作**：先读取仓库根 `README.md` → `docs/WEB_TAXONOMY.md` → 本文件 → `catalog/web-curriculum.json`，检查最新 main/PR/CI。选择优先级最高、当前仍缺的条目，从真实 Writeup 和受影响组件开始，再提交开发 PR。

- 选题已定：更新 `backlog[].status = in_progress`，记录源机器、原始软件版本与预期证据。
- 真实漏洞验收通过：补 `machines[]`，写主类别、细分技能和 CI 链接，将 backlog 标记 `done` 并在本文件更新覆盖表。
- 只完成部分：保持 `partial`，不因 PR 已合并而列为“已完成”。
- 级别不合理：基于独立体验调整暂定难度并说明原因。
- 生产仍待验收：`worker_status` 保持 `not_verified`，不能标“上线”。

**当前推荐的第一步：初级反射型 XSS；第二步：初级路径遍历；第三步：初级 NoSQL 操作符注入。**
