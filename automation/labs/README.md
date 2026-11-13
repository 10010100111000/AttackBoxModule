# 靶机镜像自动发布

复制到内容仓库的一套工具。维护一份 `lab.yml`，无需在 Actions 再写镜像地址。Control 和 Worker 不参与构建。

## 首次接入

1. 将 AttackBox 的 `automation/labs/`（不含 `node_modules`）和 `.github/workflows/lab-images.yml` 复制到**自己的内容仓库**，一并提交。内容仓库不需要其余 AttackBox 源码。
2. 内容仓库默认分支使用 `main`。如果不同，修改工作流中的 `branches`、分支判断和基线查询的 `branch` 三处。
3. 启用 GitHub Actions。工作流使用自带的 `GITHUB_TOKEN`，发布任务已声明 `packages: write`，不需要把自己的 PAT 填进代码。组织策略仍需允许此权限；若复用已有 GHCR package，须在 package 的 Actions access 中授权该内容仓库。
4. 创建下方目录并提交到 `main`。Actions 自动发现并构建；也可在 Actions 的 `lab-images` 手动运行，留空构建全部或填写一个目录。
5. 首次 GHCR package 默认私有。在 GHCR 确认可见性；保持私有时，按 [Worker 私有镜像配置](../../README.md#靶机镜像与私有仓库) 配置镜像读取凭据。复制到内容仓库后，该文档链接应改为 AttackBox 仓库地址。
6. 构建发布成功后，在 AttackBox 后台同步内容、准备到节点，然后发布教程。更新同一镜像标签后点击“更新镜像”。流水线不替管理员操作线上平台。

```text
challenges/http-lab/
├── HTTP练习.md
├── lab.yml
├── Dockerfile
└── files/
    └── index.html
```

`lab.yml`（把 `yourname` 换成 GitHub 用户或组织名，小写）：

```yaml
name: HTTP 练习环境
image: ghcr.io/yourname/http-lab:latest
port: 80
limits:
  memory: 128
  cpu: 0.5
  pids: 64
```

`Dockerfile`：

```dockerfile
FROM nginx:1.27-alpine
COPY files/index.html /usr/share/nginx/html/index.html
HEALTHCHECK --interval=2s --timeout=1s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
```

`files/index.html` 可以先写一行 `<h1>HTTP Lab</h1>`。软件安装、多个服务的启动顺序、初始化数据和日志仍由 Dockerfile、entrypoint 或 supervisord 管理；平台只约定镜像和运行参数。不要依赖容器启动后联网下载依赖。

## 自动化边界

- 自动发现任意目录中的 **`Dockerfile` + 一个 `lab.yml` / `lab.yaml`**。只填预制镜像、没有 Dockerfile 的声明可照常导入平台，但不参与构建。
- `image` 是唯一推送目的地，必须是 `ghcr.io/<当前仓库所有者>/<package>:<tag>`。不同靶机使用不同 package；发布目标不支持 digest 或保留的 `sha-` 标签。平台运行预制镜像仍支持其他镜像仓库和 digest。
- 推送到 `main` 时，仅构建自上一次成功发布流程以来有改动的目录。删除、重命名构建文件也会触发。首次运行或基线不存在时构建全部；工作流、工具更新也重建全部。
- 同目录下直接放置的 `.md` 是教程，单独修改不重建镜像。实验所需的文本（包括 `.md`）放进 `files/` 等子目录。构建上下文限当前靶机目录；共享输入请放入镜像或各自目录，不依赖目录外文件。
- 使用 Linux x86-64 runner 和本机 Docker Engine。以 `lab.yml` 的资源限制、`env` 和内部网络测试容器，不挂载宿主目录，不发布宿主端口。CI `env` 值须为单行；多行配置写入镜像文件。不要在 Git 中保存真实生产密钥。
- 容器必须持续运行、入口 `port` 可建立 TCP 连接；声明 HEALTHCHECK 时还需 healthy。默认等待最多 60 秒。特殊慢启动镜像可在工作流 check 命令添加 `--timeout 120`，上限 600 秒。它验证启动，不代替教学场景和答案验收。
- 先构建、再测试、最后推送**已测试的同一镜像 ID**。生成 `sha-<完整提交>` 标签和 `lab.yml` 中的固定标签，结果显示在 Actions Summary。标签可被覆盖，真正不可变的标识是镜像 digest。失败时不会进入推送步骤，临时容器与网络会清理。
- 自动发布只运行仓库 `main`，没有 PR 自动发布、自动部署或 Worker 在线构建。可信作者的 Dockerfile 会在 runner 中执行，不要开放给不受信任的提交者。

## 本地校验

需要 Node 22+、Linux、本机 Docker Engine。使用 Docker 当前配置的 daemon/context；无需先登录 GHCR 就能构建和测试。

```bash
npm ci --prefix automation/labs
npm test --prefix automation/labs
node automation/labs/cli.mjs plan --owner yourname --revision "$(git rev-parse HEAD)"
docker build -t ghcr.io/yourname/http-lab:latest challenges/http-lab
node automation/labs/cli.mjs check --directory challenges/http-lab
```

`plan` 不构建、不推送。`check` 不访问 GHCR。需要测试清理和实际容器行为时，可运行 `LAB_DOCKER_TEST=1 npm test --prefix automation/labs`；它使用 `nginx:1.27-alpine` 构建临时测试镜像并在结束时清理，不推送镜像。

作者字段规则由 `lab-spec.mjs` 定义，Control 直接复用。完整内容规范见 AttackBox 的 `docs/content-authoring.md`。发布任务以 `main` 最新内容为准，再锁定该提交完成构建、测试和推送，避免排队或重跑旧任务把标签回退。更新工具时完整替换此目录和工作流，避免两端契约分叉。
