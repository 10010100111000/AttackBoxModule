# AttackBoxModule — trytopwn Web 靶机题库

**统一的 Web 靶机设计与开发计划：[《Web 靶机全套设计与开发计划》](docs/WEB_LAB_DESIGN.md)。**

这是每次“继续下一台靶机”必须先阅读的入口：**31 类技术专题、219 个细分知识目标、初/中/高训练梯度、现有覆盖、尚缺场景、真实 HTB/OffSec/Vulhub 原题候选与下一台选题流程。** Docker、Flag、CI、Worker 是选题落地的验收条件，不是题库设计的主体。

机器及候选的**实时主清单**：[catalog/web-curriculum.json](catalog/web-curriculum.json)；技术知识的**唯一技能库**：[catalog/web-competencies.json](catalog/web-competencies.json)。机器实现位于 [labs/](labs/)，平台挑战正文位于 [challenges/](challenges/)，所有 CI 的实际结果请查看 [.github/workflows/](.github/workflows/)。

**验证边界**：CI 仅检查构建、启动、healthcheck、普通功能与结构一致性，不执行利用、获取 Flag、提权或自动攻击链。完整流程由人工验收，未验收必须如实标记；历史 CI 成功不自动转换为人工通过。

**工作原则**：先发现缺少的细分技术，再评估真实来源与场景增量，然后在独立 PR 中完成真正受影响的组件、自然侦察、按题目实现的完整目标路径与基础 GitHub Actions CI；完整流程采用人工验收并单独记录证据；真实 Worker 与生产发布需另外验证。不限每类机器数，不允许假漏洞、假提权、容器逃逸或公网暴露故意脆弱服务。
