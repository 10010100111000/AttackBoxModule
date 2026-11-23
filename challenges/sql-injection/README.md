# SQL 注入专题 — 统一设计入口

> 本目录保留为历史专题索引，不再存放八份重复的“设计占位”文件。**SQLi 的技能目标、8 个原始选题、对应现有靶机与后续优先级统一维护于 [《靶机设计与交付规范》§8.1](../../docs/LAB_DESIGN.md#81-sql-注入15-个技能目标)。**

**唯一开发状态数据**：[web-curriculum.json](../../catalog/web-curriculum.json)；**15 个 SQLi 技能 ID**：[web-competencies.json](../../catalog/web-competencies.json)。

已有真实实现包括 [Union](../../labs/union/)、[Validation](../../labs/validation/)、[Pebbles](../../labs/pebbles/) 和部分验收的 [GoodGames](../../labs/goodgames/)。Pebbles 的原版 ZoneMinder 与服务还原细节保留在 [RECONSTRUCTION.md](../../labs/pebbles/RECONSTRUCTION.md)，属于单台机器的技术证据，不是另一份全局计划。

> 注意：本目录 README 不会同步为平台挑战。新增靶机应在 `labs/<slug>/` 完成真实源码、Dockerfile、健康检查、Flag 和完整 CI 后，才按需要在 `challenges/<category>/<slug>/<title>.md` 创建正式题面。
