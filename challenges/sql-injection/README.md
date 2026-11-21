# SQL 注入专题（规划中）

这是**题目设计和目录占位**，不是已完成的靶机、可同步挑战或官方 HTB/OffSec 镜像。

每个子目录先保留 README.md；正式开发并通过复现测试后，才放入唯一的挑战正文 Markdown，并在 `labs/<slug>/` 交付独立的靶机工程。平台内容同步忽略 README.md。

| 顺序 | 目录 | 主考点 | 参考 |
| --- | --- | --- | --- |
| 1 | [01-credential-gate](./01-credential-gate/) | 登录 SQL 注入及权限变化 | PG Cockpit、HTB Magic |
| 2 | [02-union-ledger](./02-union-ledger/) | 回显 SQLi、查询结构判断和信息提取 | HTB Union |
| 3 | [03-blind-recovery](./03-blind-recovery/) | 布尔/时间盲注与状态判断 | HTB Usage |
| 4 | [04-asset-gallery](./04-asset-gallery/) | SQLi 作为第一道关口，上传解析作为第二关口 | HTB Magic |
| 5 | [05-source-trail](./05-source-trail/) | 从实际查询逻辑定位注入并确认数据库权限 | PG Hawat |
| 6 | [06-socket-ledger](./06-socket-ledger/) | 初始突破之后才出现的 WebSocket 注入入口 | HTB Soccer |
| 7 | [07-monitor-console](./07-monitor-console/) | 服务信息、管理 API 与真实产品 SQLi 的组合 | HTB Monitored |
| 8 | [08-camera-database](./08-camera-database/) | 数据库角色权限、文件写入和 Linux 权限隔离 | PG Pebbles |

## 统一要求

- 每题必须指定**唯一的主考点**、首次可见入口、关键转折和预期获胜条件。
- 真实软件漏洞须固定确切的受影响版本并在隔离环境实测；不能以伪造接口冒充 CVE。
- 同一专题中不同机器应有明显的技术差异，而不只是换网页风格或参数名。
- 正式题目提交前：构建脚本、健康检查、动态 Flag、重置测试、完整 Writeup 与许可检查均需过关。
- 单独 Web 挑战不强制 Root；完整 Linux 机器的低权限与 Root 阶段必须真实隔离。
- 不要将未验证环境、固定 Flag、真实凭据、Exploit 答案或来源素材直接发布到公开仓库。

参考内容编写规范：`attackbox/docs/content-authoring.md`（另一个仓库）；本仓库已有 `challenges/startpoint/` 与 `labs/` 结构可作样例。
