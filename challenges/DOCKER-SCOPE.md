# 当前靶场运行范围：Linux Docker

> 状态：设计约束。仅用于内容团队选题与复现，不作为学员挑战导入。

## 仓库现状（2026-11-22 核查）

- `AttackBoxModule/labs/` 已有 `base`、`bike`、`cursed-stale-policy`、`devvortex`、`funnel`、`goodgames` 等 Linux Docker 靶机；部分 README 明确说明环境尚未经实际构建或端到端验证。
- `.github/workflows/lab-images.yml` 搜索 `labs/**/Dockerfile`，在 Linux/amd64 上构建镜像，并通过无网络容器执行启动与 HEALTHCHECK 测试；手动发布 GHCR。
- `attackbox/docs/content-authoring.md` 规定 `challenges/<category>/<slug>/<title>.md` 是平台题面，`labs/<slug>/Dockerfile` 是镜像构建入口。README 不会作为正式题目同步。
- `attackbox/docs/image-publishing.md` 仍使用固定镜像 Flag 与 `quiz.answer` 静态验证。动态 Flag 是后续需要改造的目标，不是已经完成的生产功能。
- 金盘 Btrfs + Linux Namespaces 属于学员 AttackBox 的运行方式，不能据此假定靶机也使用相同运行机制。靶机使用 Docker，由 Worker 调度。

## 当前准入

1. 仅 Linux amd64 Docker 靶机；不制作 Windows/AD、需真实 Windows 主机的 MSSQL/IIS 利用链、容器逃逸或宿主内核提权。
2. 默认一个靶机一个 Docker 镜像，一个学员一个独立实例。多进程/多服务仍放在单容器，除非后续核实 Worker 支持多容器编排。
3. 可制作独立 Web 挑战（单 Flag）或 Linux 全流程靶机（低权限 + Root），不能强行把应用级漏洞扩展成 Root。
4. 优先真实开源项目和受影响版本；构建脚本、依赖锁定、漏洞实际复现、健康检查、重置与隔离测试不可缺。
5. 容器 Root 只代表容器内特权；SUID、Capabilities、sudo、systemd 等链需按生产 Worker 的安全限制验证，无法安全复现时调整选题。
6. 开发环境不得把故意脆弱服务公开暴露到互联网；不使用宿主 Docker socket、宿主根目录挂载或特权容器来修补题目设计。

## 当前专题

- `sql-injection/`、`file-security/`、`authentication/`、`ssrf-internal/`
- `code-execution/`、`network-services/`、`linux-privilege-escalation/`、`integrated/`

Windows/AD 仅保留为将来具备 KVM/Windows 环境时的研究方向，不属于当前 Git 挑战分类。
