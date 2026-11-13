---
category: Web 安全
level: medium
summary: 围绕 Content-Security-Policy (CSP) 策略绕过与 XSS 设计的 Web 挑战。通过构造 Payload 绕过策略限制，诱导巡检 Bot 访问并窃取管理员 Cookie 中的 Flag。
lab: .
---

# 挑战背景

本挑战模拟了一个部署了严格内容安全策略（Content-Security-Policy, CSP）的现代化 Web 应用。后端采用 Fastify 框架构建，前端结合 Vite 打包，同时集成 Redis 任务队列与 Chromium 无头巡检机器人（Bot）。

管理员为应用启用了自动化巡检服务，巡检 Bot 会定期访问学员提交的页面链接。

# 任务目标

1. 审查后端应用中关于 CSP 策略的生成逻辑与缓存行为。
2. 挖掘存在的策略缺陷或绕过路径，构造满足 XSS 执行条件的恶意 Payload。
3. 提交利用链接给后台巡检 Bot，迫使其在访问页面时外带携带在 Cookie 中的系统 Flag。

```quiz
title: 获取管理员 Flag
kind: flag
prompt: 构造有效 Payload 绕过 Fastify 的 CSP 策略限制，诱导巡检 Bot 访问你的利用载荷，获取管理员 Cookie 中的 Flag。
answer: "HTB{f4k3_fl4g_f0r_t35t1ng}"
match: trim
hint: 仔细审查 Fastify 中间件中的 CSP 策略生成与缓存机制，利用 Bot 携带的 Cookie 实施外带。
```
