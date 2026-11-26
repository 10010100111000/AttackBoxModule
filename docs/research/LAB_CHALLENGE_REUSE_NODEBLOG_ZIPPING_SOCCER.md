# NodeBlog / Zipping / Soccer — Lab 复用与 Challenge 独立性审查

**日期：2026-11-26**  
**范围：只读源码、题面、Flag 存放方式和既有 CI 证据；本次没有修改 Dockerfile、应用代码、脚本、Flag、题面或 Worker。**

## 结论摘要

| Lab | 已确认的真实 Web 机制 | 当前 Flag | 是否建议拆成多道独立 Challenge |
| --- | --- | --- | --- |
| NodeBlog | MongoDB NoSQL 认证绕过 → libxml2 XXE 源码读取 → node-serialize 0.0.4 不安全反序列化执行 | `/home/nodeblog/user.txt`，nodeblog UID 10001，0600 | **暂不拆**。一条连续链、一个最终 Web Flag；一题覆盖多个 Skill，可增加知识检查阶段 |
| Zipping | ZIP 符号链接处理 → MariaDB SQLi/FILE → PHP LFI/include | `/home/rektsu/user.txt`，www-data，0400 | **暂不拆，先验证绕题路径**。源代码显示可能直接用 ZIP symlink 读取最终 Flag，绕过后续 SQLi/LFI |
| Soccer | 原版 Tiny File Manager 上传 → Nginx vhost/config 发现 → WebSocket/MariaDB 布尔盲注 | `soccer_db.accounts.goal`；启动时由 root-owned 0400 seed 写入 | **暂不拆 Flag Challenge**。建议一题多技能，增加 vhost 与 WebSocket 协议两个 question checkpoint，最后提交一个 Web Flag |

核心结论：**多 Challenge 复用是平台能力，不是把每个漏洞阶段都切成一道题。** 这三台目前都只有一个有意义的最终 Flag。NodeBlog 和 Soccer 的自然阶段适合做同一 Challenge 的分阶段问题；Zipping 还存在需要先确认的 Flag shortcut。

---

## 1. NodeBlog

### 真实实现和漏洞入口

源码证据：

- `labs/nodeblog/routes/login.js`：登录处理将 JSON 请求体中的 `user` 和 `password` 对象直接交给 Mongoose `User.findOne()`，没有把对象操作符转换成普通字符串。后端使用真实 MongoDB，不是模拟查询器。
- `labs/nodeblog/routes/articles.js`：登录后访问 XML 导入；使用 `libxmljs2` 调用真实 libxml2，设置 `noent: true`，解析 XML 外部实体。
- `labs/nodeblog/server.js`：使用上游 `node-serialize`；`authenticated()` 在检查 MD5 签名前先调用 `serialize.unserialize()`，因此不安全反序列化的 IIFE 可以先执行。
- `labs/nodeblog/Dockerfile`：真实 MongoDB 8、Node 20、libxmljs2 0.37.0、node-serialize 0.0.4；服务以 nodeblog UID 10001 运行。
- `labs/nodeblog/seed.js`：初始化 admin 账号和文章。

### Flag 可达性

- 当前只有一个 Flag：`/home/nodeblog/user.txt`。
- 文件 owner 为 nodeblog，权限 0600；Node Web 进程也以 nodeblog 运行。
- `NODEBLOG_USER_FLAG` 在入口脚本写入文件后即 unset；Worker 不负责生成、校验或判题。
- 只有最终不安全反序列化导致的真实命令执行阶段，才获得读取该文件的能力。NoSQL 绕过和 XXE 本身没有独立 Flag。

### Challenge 独立性判断

不建议拆成三个 Flag Challenge。三个漏洞是严格递进的发现/利用路径，不是三个拥有独立最终目标的环境：

1. NoSQL 操作符绕过登录，取得应用身份。
2. XML 导入触发真实 XXE，读取应用源码并发现易受攻击的序列化依赖。
3. Cookie 反序列化执行，取得 Web 服务账户能力并读取唯一 Flag。

推荐保持一个综合 Web Challenge，主考点设为 NoSQL 认证绕过，次考点为 XXE 和不安全反序列化。可在同一 Challenge 内增加非 Flag 的知识检查，例如从 XML 源码披露中识别依赖包和版本。不要为了拆题而添加没有真实来源的 Flag 文件。

### 既有证据和限制

README 记录两次全新容器的独立 HTTP 利用链 CI 通过，包含真实 MongoDB、XXE、node-serialize 执行和 Flag 读取。它不是人工验收，也不是 Worker 发布验收。当前 `.release-blocked` 仍存在。

---

## 2. Zipping

### 真实实现和漏洞入口

源码证据：

- `labs/zipping/site/upload.php`：上传处理使用 PHP ZipArchive，要求 ZIP 仅有一个扩展名为 PDF 的条目；随后执行真实 `unzip -j`，并将提取出的文件 rename 到 Apache 可访问的 uploads 目录。
- `labs/zipping/Dockerfile`：Apache 目录明确启用 `Options FollowSymLinks`；uploads 目录由 www-data 写入。
- `labs/zipping/site/shop/product.php`：数字过滤正则存在换行绕过条件，随后将输入拼入真实 MariaDB 查询。PDO 使用 emulated prepares。
- `labs/zipping/db/init.sql`：shop 数据库用户具有 SELECT 和 FILE 权限。
- `labs/zipping/site/shop/index.php`：通过 `file_exists($page . '.php')` 后执行 PHP `include`，形成真实 LFI/include 执行边界。

### Flag 可达性与潜在 shortcut

当前唯一 Flag 为 `/home/rektsu/user.txt`，owner 是 www-data，mode 0400。最终 PHP include/RCE 以 www-data 身份运行，因此可以读取它。

但源码还显示一个高优先级风险：

1. ZIP 条目名只需要是一个 basename 且以 `.pdf` 结尾；basename 检查本身不验证该条目是不是 symlink。
2. README 说明当前 Info-ZIP 解包行为会保留 Unix symlink。
3. 解包后通过 `file_exists()` 检查，并将条目 rename 到 uploads。
4. Apache 启用了 FollowSymLinks。
5. 当前 Flag 对 www-data 可读。

因此，**一个指向 `/home/rektsu/user.txt` 的绝对 ZIP symlink 可能在上传阶段就直接读取最终 Flag**。这是基于代码和权限的高置信度风险判断，但本次没有实际构建容器并复现该请求，不能把它写成已经证实。

### 隔离验证结果：直接 Flag 读取已确认（2026-11-26）

GitHub Actions 临时 Ubuntu Runner 已使用**未修改的 Zipping 镜像**完成验证：

- 在内部 Docker 网络启动目标，注入唯一测试 Flag `TTP{zipping_symlink_probe_2026}`。
- 生成一个 ZIP，唯一条目名为 `resume.pdf`，Unix symlink 目标为 `/home/rektsu/user.txt`。
- 通过正常 `/upload.php` 上传，应用返回成功和 `/uploads/2da1da9f8cf138cae5a2d14a4d148be0/resume.pdf`。
- 对该返回 URL 发起普通 HTTP GET，响应正文包含唯一测试 Flag。
- 整个过程没有使用 SQLi、MariaDB FILE、PHP LFI 或命令执行。
- Runner 最后清理目标容器、内部网络和测试镜像。

<badge>结论：DIRECT_FLAG_READ_CONFIRMED</badge>

证据：[GitHub Actions run 45782449750](https://github.com/10010100111000/AttackBoxModule/actions/runs/45782449750)，测试提交 `208b776f643693c5b44130335d93298b17df9fd0`。同一提交上的常规 Lab 镜像构建/启动检查也通过：[run 45782449684](https://github.com/10010100111000/AttackBoxModule/actions/runs/45782449684)。

这证实了 ZIP symlink 上传路径可以直接读取最终 Flag，原先设计的 SQLi/FILE/LFI 阶段并非取得 Flag 的必要条件。

### 后续决策（尚未修改运行代码）

必须先决定题目目标：

1. **将 ZIP symlink 文件读取作为题目核心**：把它明确设计为文件处理专项，SQLi/LFI 留作环境中的额外漏洞或后续训练目标；但不能宣称用户必须完成 SQLi/LFI 才能得到现有 Flag。
2. **保留 SQLi/FILE/LFI 为必经目标**：需要调整 Flag 的存放/可达边界或题目机制，使公开上传 URL 不再直接暴露最终 Flag，同时保留真实的归档处理漏洞。之后必须重新跑直接 symlink 负向测试和完整 SQLi/LFI 正向链。

本轮没有修改 Dockerfile、PHP、Flag、题面或 Worker，也没有解除发布阻断。

### Challenge 独立性判断

在 shortcut 验证前，不应把当前 SQLi/LFI 题拆成多个 Flag Challenge。

- 如果 symlink 可以直接读取 Flag，当前唯一 Flag 并不能证明 SQLi/FILE/LFI 链完成。
- 可以考虑把 symlink disclosure 作为独立的文件处理 Challenge，但后续 SQLi/LFI 题必须有独立、自然可取得的目标答案；不能复制同一个 Flag。
- 如果不希望 symlink 直接成为最终目标，则需要重新设计 Flag 的权限/存放位置或上传行为，但不能因此删除真实的 ZIP symlink 漏洞，也不能先凭空增加第二枚 Flag。

推荐暂时保留一个综合 Challenge，先完成 shortcut 负向/正向测试，再决定是否拆分。

### 既有证据和限制

README 记录两次全新实例的 CI 完整链通过：ZIP symlink 读取源码、SQLi 过滤绕过、MariaDB FILE 写入、PHP include 执行和 Flag 获取。现有 CI 说明了所测路径成功，**不等于排除了更短的直接 symlink-to-Flag 路径**。当前 `.release-blocked` 仍存在。

---

## 3. Soccer

### 真实实现和漏洞入口

源码证据：

- `labs/soccer/Dockerfile`：固定拉取原版 Tiny File Manager 2.4.3 上游提交 `1dbe7c5339ad955fcb08d01d256f591a3c83d713`，不是自制文件管理器。
- `labs/soccer/scripts/filemanager-config.php`：上传根目录设置为 `/var/www/html/tiny/uploads`。
- `labs/soccer/scripts/nginx.conf`：配置两个虚拟主机，第二个是 `soc-player.soccer.htb`。
- `labs/soccer/app/server.js`：Node ws 服务接收 JSON `id`，直接插入真实 MariaDB 查询；存在真/假票据响应差异。
- `labs/soccer/db/init.sql`：真实 MariaDB 中有 tickets 与 accounts 表，Node 使用 ticket_reader 只读账号。
- `labs/soccer/scripts/start.sh`：从 `/home/player/user.txt` 读取 Flag 并写入 `soccer_db.accounts.goal`。

### Flag 可达性

- Flag 最终保存在 `soccer_db.accounts.goal`，不是直接由上传接口返回。
- seed 文件位于 `/home/player/user.txt`，owner root，mode 0400。
- PHP 上传运行在 www-data，不能直接读取 root-owned seed。
- Node 服务以 soccerapp 用户运行，并通过 ticket_reader 数据库账号查询。
- WebSocket SQLi 的真实布尔差异可以从 accounts.goal 提取最终 Web Flag。

因此，上传 foothold 和 vhost/config disclosure 本身并没有取得 Flag；它们是发现第二个 WebSocket 服务的前置侦察路径。

### Challenge 独立性判断

推荐一条综合 Web Challenge，主考点为 WebSocket blind SQLi，次考点为文件上传、配置泄露、WebSocket 协议侦察和布尔盲注。

在同一 Challenge 中加入两个非 Flag 的 question checkpoints：

1. 从真实 Nginx 配置识别第二个虚拟主机。
2. 识别 WebSocket 的 JSON 消息字段及真/假响应。

最后通过 WebSocket SQLi 提交唯一 Flag。这样保留了真实侦察过程，也没有为了上传阶段强行创建第二枚 Flag。

### 既有证据和限制

README 记录两次全新实例通过 HTTP + WebSocket 的独立完整链 CI，使用不同的实例 Flag。Worker 网络、端口策略和 Web 后端判题仍未验收；当前 `.release-blocked` 仍存在。

---

## 4. 平台复用能力：目前能确认什么

另行只读检查了平台仓库 `10010100111000/attackbox`：

- `web/server/db/schema/challenges.ts`：Challenge 有 `target_template_id`。
- `web/server/db/schema/target-templates.ts`：target_templates 保存镜像、资源、平台和加密变量。
- `web/server/services/challenges.ts`：Challenge detail 读取关联的 target template。
- Worker 的 target model / start flow 使用 `target_id` 和 `owner_id`，Worker 本身负责容器和沙箱生命周期。

目前能确认：多个 Challenge 在数据层可以引用同一个 target template/image。

目前**不能确认**：两个不同 Challenge ID 对同一个用户是否复用同一个运行中的容器、共享网络地址和状态，或者重置一个 Challenge 是否会影响另一个 Challenge。现有 schema 中尚未看到明确的 Lab 实体或 LabChallenge 关联表。

因此必须区分：

- **镜像/模板复用**：同一个 target template 被多道题引用。
- **运行实例复用**：同一用户的多道题真正连接到同一个 Lab 实例。

前者已有字段可以表达；后者还没有从当前源码证实。下一步需要追踪 target-start API 如何生成 target_id，并用两个 Challenge ID 指向同一个模板进行验证。此项不应直接通过修改 Worker 来猜测解决。

---

## 5. 最终建议

1. NodeBlog：保持一题多 Skill，增加 question checkpoints，不拆成三个 Flag Challenge。
2. Zipping：先做 symlink-to-Flag shortcut 测试；在此之前不宣称 SQLi/LFI 阶段有独立目标。
3. Soccer：保持一题多 Skill，增加 vhost 和 WebSocket 协议两个 question checkpoints，最终一个 Web Flag。
4. 在平台确认“同模板是否同实例”之前，不批量创建多道 Challenge 指向同一模板，也不承诺用户能在多道题间共享一个运行环境。
5. 本轮只更新规划与审计记录；未修改运行代码、Flag、题面或 Worker。
