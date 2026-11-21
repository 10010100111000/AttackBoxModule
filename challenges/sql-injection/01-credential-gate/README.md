# Credential Gate — SQL 注入认证绕过

> 状态：**已有首版可运行源码，未完成 Docker / Worker 环境验收，尚未发布挑战**。

- 原创业务场景：Northstar Dispatch 物流调度与合规导出系统。
- 核心考点：登录请求中的真实 SQLite SQL 注入，利用注释改变认证查询条件。
- 初始入口：公开登录页面。
- 关键转折：以管理员身份进入控制台后，发现受限季度审计 CSV 导出。
- 完成条件：从受限报表中取得**静态**演示 Flag（最终上线前须替换）。
- 形式：**单阶段 Web 挑战**，不虚构 Linux Root 提权。
- 参考：OffSec PG Cockpit 与 HTB Magic 的认证入口模式。此题使用原创程序、界面和故事，不复制原题代码。

## 工程位置

源码放在 [labs/credential-gate](../../../labs/credential-gate/)；包含 Dockerfile、SQLite 真实业务、CSS、测试脚本和 README。默认运行在容器内 TCP 8080，单 Docker 镜像。

## 当前验收

- 已通过本地 Python 语法检查及 6 项 HTTP 集成测试。
- 未在当前环境完成 Docker 构建与 Worker 真实启动验收。
- 使用公开 **demo flag**，尚未提供可公开发布的真实挑战内容。
- 故意不创建题面 Markdown 及 quiz.answer，避免被平台错误当成正式可发布题目；静态 Flag 发布方式须在管理后台核对。

## 下一步

1. 在支持 Docker 的 CI/节点执行镜像构建、健康检查与端到端 SQLi 验证。
2. 确认端口、资源限制与 Worker 的目标网络权限兼容。
3. 准备未公开的正式静态 Flag，并核对挑战服务端判题配置。
4. 通过验收后再补正式题面 Markdown、提示和玩家可见目标。
