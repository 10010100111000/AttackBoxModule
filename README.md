# AttackBoxModule — trytopwn 靶机仓库

**唯一的靶机设计规范入口：[《trytopwn 靶机设计与交付规范》](docs/LAB_DESIGN.md)。**

这是制作靶机的必读文档：真实漏洞与来源核验、课程目标、完整侦察路径、Docker/Worker 兼容性、Flag 与管理员 Bot 边界、镜像优化、独立 GitHub Actions CI、重置和发布门禁均在其中。**以后不再按 SQLi/XSS/架构/发布流程创建平行的全局设计文档。**

## 日常工作只需要三个入口

| 入口 | 职责 |
| --- | --- |
| [**完整设计与交付规范**](docs/LAB_DESIGN.md) | 全局规则、选题方法、历史 SQLi 规划、真实验收与发布流程 |
| [Web 知识点目录](catalog/web-competencies.json) | 31 个专题、219 个技能目标、难度与专项测试要求 |
| [机器与开发计划主清单](catalog/web-curriculum.json) | 机器状态、候选、backlog、CI 证据和 Worker 验证状态 |

机器本身的具体实现存放在 [`labs/`](labs/)；正式学员题面在 [`challenges/`](challenges/)；实际验证依赖 [GitHub Actions](.github/workflows/)，目录与主清单一致性由 [校验脚本](scripts/validate_web_curriculum.py) 检查。

### 开发顺序

从设计规范和主清单选定有价值的技能缺口 → 核验上游真实源码与 Writeup → 独立分支开发 Docker 靶机 → 通过普通玩家视角的完整攻击链 CI → 记录镜像与资源数据 → 真实 Worker 网络和判题验收 → 发布。

**只设计 README、只完成 Dockerfile、或 CI 仅启动成功，都不能被称为已完成靶机。** CI 通过不代表真实 Worker 已适配。不要制作模拟 CVE、假提权链或 Docker 容器逃逸，也不得将故意脆弱靶机暴露到公网。
