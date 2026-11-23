# AttackBoxModule — trytopwn Web 靶机题库

**统一的 Web 靶机设计与开发计划：[《Web 靶机全套设计与开发计划》](docs/WEB_LAB_DESIGN.md)。**

这是每次“继续下一台靶机”必须先阅读的入口：**31 类技术专题、219 个细分知识目标、初/中/高训练梯度、现有覆盖、尚缺场景、真实 HTB/OffSec/Vulhub 原题候选与下一台选题流程。** Docker、Flag、CI、Worker 是选题落地的验收条件，不是题库设计的主体。

机器及候选的**实时主清单**：[catalog/web-curriculum.json](catalog/web-curriculum.json)；技术知识的**唯一技能库**：[catalog/web-competencies.json](catalog/web-competencies.json)。机器实现位于 [labs/](labs/)，平台挑战正文位于 [challenges/](challenges/)，所有 CI 的实际结果请查看 [.github/workflows/](.github/workflows/)。

**工作原则**：先发现缺少的细分技术，再评估真实来源与场景增量，然后在独立 PR 中完成真正受影响的组件、自然侦察、完整 Flag 路径与独立 GitHub Actions CI，CI 通过后才汇报；真实 Worker 与生产发布需另外验证。不限每类机器数，不允许假漏洞、假提权、容器逃逸或公网暴露故意脆弱服务。
