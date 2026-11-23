# AttackBoxModule — trytopwn 靶机与 Web 技能题库

本仓库维护真实受影响组件构成的 Web 安全训练靶机。**选题以知识点与真实攻击场景为核心，允许同类漏洞反复出现；只排除没有教学增量的换皮重复。**

## 以后制作靶机，请按顺序阅读

| 文件 | 作用 |
| --- | --- |
| [Web 知识分类与三级难度](docs/WEB_TAXONOMY.md) | PortSwigger Web Security Academy 的 31 专题框架，如何把一个知识点分成不同难度与输入上下文 |
| [Web 细分知识目标](catalog/web-competencies.json) | **219 个细分目标**、建议初始难度、场景与验收标准；所有专题都有记录 |
| [真实靶机的选择与评审](docs/WEB_MACHINE_SELECTION.md) | 如何从 HTB/OffSec/上游代码选择、比较并复现靶机；允许同技能多个不同场景 |
| [覆盖现状和滚动路线图](docs/WEB_ROADMAP.md) | 目前 17 个目录、SQLi/XSS 等细分缺口、可复现机器候选与后续顺序 |
| [现有靶机及开发队列](catalog/web-curriculum.json) | 已有靶机的主标签、场景特征、CI/Worker 验收状态、候选清单和滚动需求 |
| [清单一致性检查](scripts/validate_web_curriculum.py) | GitHub Actions 验证官方专题、细分技能、机器目录、候选引用及待开发任务的编号；见 [工作流](.github/workflows/web-curriculum.yml) |
| [平台与靶机职责边界](docs/PLATFORM_FLAG_BOUNDARIES.md) | Web 后端判题、Worker 只调度、Flag 自靶机取得；XSS 管理员访问属于题目本身，不是 Worker 的 Bot |

## 选题的固定工作方式

1. **先选知识目标**：确定 `topic_id`、`skill_id`、建议难度和具体场景；不要只报“制作一台 SQLi 靶机”。
2. **再选择真实靶机**：可信来源、原始 Writeup、受影响的软件/依赖版本，核实侦察路线和 Docker/Linux 可行性。
3. **允许有价值的重复**：例如 UNION、二阶 SQLi、布尔盲注、时间盲注、WebSocket 盲注可以同时收录；即使同一种 UNION，也可按数据库方言、输入面、过滤约束再做不同训练。
4. **逐台验证**：独立攻击者从扫描/枚举开始，验证真实漏洞与目标 Flag。镜像大小、健康检查、环境清除和隔离均进入 CI。
5. **区分三种完成状态**：源码合并、靶机完整攻击链 CI、生产 Worker 实测通过；三者不可相互替代。

现有机器和今后的开发需求只作**滚动目录**，不设置每类最多几台或下一批只能九台的配额。安全约束不变：不伪造漏洞/提权，不做 Docker 容器逃逸，不允许有漏洞的服务直接对公网开放。

> 规划快照：2026-11-23。GitHub 代码合并不自动代表 Worker 可以正式发布；例如 Editorial 仍有独立的 Worker 发布保护标记。
