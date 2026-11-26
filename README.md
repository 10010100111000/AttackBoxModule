# AttackBoxModule — trytopwn Web 靶机题库

**统一的 Web 靶机设计与开发计划：[《Web 靶机全套设计与开发计划》](docs/WEB_LAB_DESIGN.md)。**

这是每次“继续下一台靶机”必须先阅读的入口：**31 类技术专题、219 个细分知识目标、初/中/高训练梯度、现有覆盖、尚缺场景、真实 HTB/OffSec/Vulhub 原题候选与下一台选题流程。** Docker、Flag、CI、Worker 是选题落地的验收条件，不是题库设计的主体。

机器及候选的**实时主清单**：[catalog/web-curriculum.json](catalog/web-curriculum.json)；技术知识的**唯一技能库**：[catalog/web-competencies.json](catalog/web-competencies.json)。机器实现位于 [labs/](labs/)，平台挑战正文位于 [challenges/](challenges/)，所有 CI 的实际结果请查看 [.github/workflows/](.github/workflows/)。

**验证边界**：每台靶机除构建、启动、healthcheck 和普通功能检查外，必须由独立攻击端通过隔离网络走完真实题目路径，并验证取得的 Flag 与当前实例及 Challenge 答案一致。禁止使用模拟漏洞、测试后门、`docker exec` 或挂载目标文件系统直接读取 Flag。历史 CI 成功不自动转换为新标准下的端到端通过。

**工作原则**：先发现缺少的细分技术，再评估真实来源与场景增量，然后在独立 PR 中完成真实组件、自然侦察、题目路径和专属 GitHub Actions 端到端验收。CI 必须从网络入口取得正确 Flag 才算通过；真实 Worker 与生产发布另行验证。不限每类机器数，不允许假漏洞、假提权、容器逃逸或公网暴露故意脆弱服务。
