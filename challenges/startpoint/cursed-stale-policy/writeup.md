# Cursed Stale Policy — Writeup

## 目标

通过 CSP 分析平台的正常交互发现策略 nonce 被跨请求复用，再利用真实的管理员 Puppeteer/Chromium 审阅流程执行存储型脚本，读取管理员浏览器中的 Web Flag。

## 1. 观察 CSP 响应头

访问 CSP Analyser 首页，检查 HTTP 响应头中的 Content-Security-Policy。记录 script-src 中的 nonce。

随后访问 Guidelines 页面，再次检查响应头。两次请求使用了相同的 nonce。正常情况下，nonce 应当为每个 HTML 响应重新生成；长期复用会使原本一次性的授权值失去时效性。

## 2. 检查客户端与 WebSocket 交互

首页使用 WebSocket 与后端通信。检查前端发送的消息类型，可以发现读取默认 CSP 和提交 XSS 审阅任务的操作。

通过 fetch_default_csp 读取 Redis 中缓存的 CSP 策略，并确认其中的 nonce 与 HTTP 响应头一致。

## 3. 提交带 nonce 的审阅内容

平台提供 Trigger Bot 功能。将带有已观察 nonce 的脚本作为审阅内容提交。脚本在同源页面中访问应用的回调路由，并将执行结果记录到应用的请求历史。

## 4. 理解管理员浏览器的执行上下文

后端将审阅任务放入 Bull 队列。独立 Worker 进程启动真实 Puppeteer/Chromium，并访问内部的 XSS 审阅页面。

Bot 在访问页面前设置管理员 Flag Cookie。该 Cookie 没有启用 HttpOnly，因此脚本可以通过浏览器脚本上下文读取。

浏览器收到的 CSP nonce 与攻击者此前观察到的 nonce 相同，带 nonce 的脚本因此能够执行。

## 5. 从回调记录中取得 Flag

脚本向同源回调路由提交浏览器执行结果。后端把请求参数写入 Redis 请求历史，并通过 WebSocket 广播更新。

使用 fetch_logs 读取请求记录，在回调参数中找到管理员 Flag，提交精确值。

## 漏洞链总结

1. CSP nonce 被 Redis 长期缓存并跨响应复用。
2. WebSocket 暴露缓存的默认 CSP 策略。
3. 玩家可以提交存储型 XSS 审阅任务。
4. 真正的管理员 Chromium 在带有可读 Flag Cookie 的上下文中打开任务。
5. nonce 重用使脚本通过 CSP 检查。
6. 同源回调记录泄露管理员 Cookie。

## 关键源码

- challenge/backend/middleware/cspMiddleware.js：为响应设置 CSP。
- challenge/backend/utils/redis.js：缓存策略、审阅队列和回调记录。
- challenge/backend/routes/websocket.js：公开的 CSP 查询、XSS 触发和日志读取操作。
- challenge/backend/workers/worker.js：Bull 审阅 Worker。
- challenge/backend/bot/bot.js：真实 Puppeteer/Chromium 与管理员 Cookie。
- challenge/backend/routes/xss.js：按审阅任务加载提交内容。

## 复现边界

这是基于真实 Fastify、Redis、Bull、Puppeteer 和 Chromium 行为构建的故意脆弱训练应用。漏洞来自应用对 CSP nonce 的错误缓存与复用，不声称复现某个第三方产品 CVE。
