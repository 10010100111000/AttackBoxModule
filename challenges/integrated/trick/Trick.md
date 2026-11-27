---
summary: 一家企业将多个内部业务系统部署在同一网络中。请从公开服务开始进行枚举，逐步识别不同应用之间的信任边界，并取得系统的两个 Flag。
level: intermediate
lab: trick
---

# 场景

一家企业为不同部门部署了独立的内部业务系统。外部只提供有限的网络入口，但不同服务之间共享部分基础设施和身份信息。

请从目标公开的网络服务开始，观察 DNS、Web 应用和系统服务之间的关系。不要假设不同服务使用相同的权限或运行身份。

# 任务

完成对目标环境的安全评估，取得普通系统账户权限，并进一步验证系统内部的特权配置风险。

\`\`\`quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: |
  从目标服务的正常入口开始调查，沿着真实业务和身份边界取得普通系统账户权限，并读取该账户家目录中的 Flag。
answer: "TTP{aaaaaaaaaaaaaaaa}"
match: trim
\`\`\`

\`\`\`quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: |
  在取得普通系统账户后，检查系统服务、文件权限和管理操作边界，利用真实存在的配置缺陷取得 Root Flag。
answer: "TTP{bbbbbbbbbbbbbbbb}"
match: trim
\`\`\`
