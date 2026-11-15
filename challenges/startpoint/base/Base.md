---
level: medium
summary: 某企业上线了一套单页展示站点，后台系统仍处于测试阶段。你需要从外部边界侦察入手突破访问控制，并进一步在主机内部提权夺取最高权限。
---

# 任务目标

探测目标 Web 资产，发现并利用安全缺陷突破认证与代码执行防护，获取主机初始访问权限。搜集主机内部凭据与环境配置，完成本地提权，获取系统最高控制权。

```quiz
title: 获取用户权限 (User Flag)
kind: flag
prompt: 突破目标系统外围边界并获取主机立足点，读取并提交普通用户家目录中的 Flag。
answer: "ATB{b4s3_u53r_fl4g_f0r_t35t1ng}"
match: trim
hint: 细致的目录扫描与资产勘测往往能发现遗留的蛛丝马迹；留意目标服务运行时的语言环境特征。
```

```quiz
title: 系统特权提升 (Root Flag)
kind: flag
prompt: 审计主机内部环境与特权分配策略，提权至 root 用户并提交 `/root/root.txt` 中的 Flag。
answer: "ATB{b4s3_r00t_fl4g_f0r_t35t1ng}"
match: trim
hint: 关注凭据在系统内部的复用情况，以及当前用户被允许执行的特殊管理指令。
```
