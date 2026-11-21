# SQL 注入专题（规划中）

这是**待复现的原题研究目录**，不是已完成的靶机、可同步挑战或官方 HTB/OffSec 镜像。不得重新发明一个自制漏洞应用，冒充原题复现。

**首个研究对象为 OffSec PG Pebbles**：先读 [原题服务与攻击链复原方案](../../labs/pebbles/RECONSTRUCTION.md)，确认上游 ZoneMinder 1.29.0 与 Ubuntu 16.04 的实际版本和服务配置，然后验证 Docker 环境。其他目录只是先前选题，必须先补齐原题技术栈和侦察路径，才能决定是否制作。平台内容同步忽略 README.md。

| 顺序 | 目录 | 主考点 | 参考 |
| --- | --- | --- | --- |
| 1 | [01-credential-gate](./01-credential-gate/) | **暂停：先前原创登录应用不符合原题复现要求** | PG Cockpit 原生服务核对后再决策 |
| 2 | [02-union-ledger](./02-union-ledger/) | 回显 SQLi、查询结构判断和信息提取 | HTB Union |
| 3 | [03-blind-recovery](./03-blind-recovery/) | 布尔/时间盲注与状态判断 | HTB Usage |
| 4 | [04-asset-gallery](./04-asset-gallery/) | SQLi 作为第一道关口，上传解析作为第二关口 | HTB Magic |
| 5 | [05-source-trail](./05-source-trail/) | 从实际查询逻辑定位注入并确认数据库权限 | PG Hawat |
| 6 | [06-socket-ledger](./06-socket-ledger/) | 初始突破之后才出现的 WebSocket 注入入口 | HTB Soccer |
| 7 | [07-monitor-console](./07-monitor-console/) | 服务信息、管理 API 与真实产品 SQLi 的组合 | HTB Monitored |
| 8 | [08-camera-database](./08-camera-database/) | **当前优先：真实 ZoneMinder 1.29.0、隐藏 /zm、MySQL 文件写入和 UDF** | PG Pebbles |

## 当前平台约束（已核对仓库）

- **当前只上线 Linux Docker 靶机。** 暂不纳入 Windows、Active Directory、MSSQL Windows 专属链、内核提权或容器逃逸题目。
- 目录分工：`challenges/<category>/<slug>/` 存学员题面及 Writeup，`labs/<slug>/` 存 Dockerfile、启动脚本、真实服务、测试与素材。不要在规划目录中添加 Dockerfile 触发镜像构建。
- Docker 镜像由 `.github/workflows/lab-images.yml` 根据 `labs/**/Dockerfile` 构建，采用 Linux/amd64；运行实例由平台 Worker 管理。**一题一镜像、一实例一容器**为目前最稳妥的默认设计。确实需要多服务时可在同一容器内运行真实进程，使用内部回环端口和独立账户；不预设平台支持 Compose 多容器编排。
- 优先选择 PHP、Python、Node.js、Ruby、Java、SQLite/MySQL/PostgreSQL、FTP/SMTP/SNMP/Redis 等在 Linux 容器里可复现的场景。涉及 systemd、SUID、Capabilities、sudo 时，必须先在平台真实容器权限配置下做端到端验证；不能为复现强行放开宿主机权限。
- **现阶段使用静态 Flag**，遵循当前 `attackbox/docs/content-authoring.md` 中的 `quiz.answer` 判题机制。用户、Root 是否双 Flag 取决于原题真实利用链，不增加不必要的阶段。

## 统一要求

- 每题必须指定**唯一的主考点**、首次可见入口、关键转折和预期获胜条件。
- 真实软件漏洞须固定确切的受影响版本并在隔离环境实测；不能以伪造接口冒充 CVE。
- 同一专题中不同机器应有明显的技术差异，而不只是换网页风格或参数名。
- 正式题目提交前：**真实来源/版本/前端与服务端口复原**、构建脚本、健康检查、静态 Flag、重置测试、完整 Writeup 与许可检查均需过关。
- 单独 Web 挑战不强制 Root；完整 Linux 机器的低权限与 Root 阶段必须真实隔离。
- 不将未验证环境、正式 Flag、真实凭据、未授权原题素材直接发布到公开仓库。开发期可使用明确标识的演示 Flag，但发布时必须有正确的私密初始化流程。

参考内容编写规范：`attackbox/docs/content-authoring.md`（另一个仓库）；本仓库已有 `challenges/startpoint/` 与 `labs/` 结构可作样例。
