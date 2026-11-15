# 靶机镜像自动发布

将本目录的源码与 [lab-images.yml](../../.github/workflows/lab-images.yml) 工作流复制到内容仓库，开启 GitHub Actions。模块、挑战和参考资料共用一个内容仓库；每个靶机的 Dockerfile 与 lab.yml 位于相同目录。

```text
challenges/startpoint/
  base/
    Base.md
    lab.yml
    Dockerfile
    entrypoint.sh
    files/
  web-lab/
    Web实验.md
    lab.yml
    Dockerfile
```

`lab.yml` 最小声明：

```yaml
image: ghcr.io/yourname/attackbox-labs:base
```

可选参数只有 `env`、`limits.memory`、`limits.cpu`、`limits.pids`，与服务端共用 `lab-spec.mjs` 验证。练习场景、服务端口和使用方法写在正文。完整作者规范见 [内容编写指南](../../docs/content-authoring.md)。

不同靶机可以共用 `ghcr.io/yourname/attackbox-labs`，但必须使用不同 tag。发布器同时推送稳定 tag 和 `<tag>-sha-<完整提交号>`，避免同一次提交中不同靶机覆盖彼此；构建缓存也按完整镜像地址隔离。`image` 必须属于当前内容仓库所有者。

GHCR 的可见性是 package 级别。首次在 GitHub 将共享 package 设为公开一次，后续 tag 一并公开。Actions 已配置 `packages: write`，使用自带的 `GITHUB_TOKEN`。已有 package 需要允许该仓库的 Actions 写入。

工作流只对新增或构建输入变化的靶机重新构建。直接位于靶机目录的 Markdown 是教程；实验用 Markdown 放在 `files/` 等子目录，参与构建变更判断。自动化代码变化会重新构建所有靶机。镜像仓库中的历史版本由作者管理。

镜像构建完成后，在独立 internal 网络中以实际资源限制启动测试实例。验证容器持续运行，存在 `HEALTHCHECK` 时还必须通过检查。容器通过测试私网运行，使用 Dockerfile 定义的健康检查。测试实例和网络会被清理，只有通过检查的镜像 ID 才允许推送。

服务启动、依赖和初始数据属于镜像。多进程可使用 entrypoint 或 supervisord 管理。建议为网络服务提供实际就绪检查，例如：

```dockerfile
HEALTHCHECK --interval=5s --timeout=2s CMD curl -fsS http://127.0.0.1/health || exit 1
```

等待 Actions 发布完成，再同步 Git 内容；同步后 Worker 自动预热，学员启动时也可按需拉取。
