# Bike - 单容器复现靶机

按 Bike.pdf 的服务与漏洞链路搭建的教学环境。**仅限本机隔离网络，禁止公网部署。**

## 启动

```bash
docker build -t bike-lab .
docker run -d --name bike-lab --restart unless-stopped \
  -p 127.0.0.1:8080:80 -p 127.0.0.1:2222:22 bike-lab
```

浏览器访问 `http://127.0.0.1:8080/`。
SSH 用于端口枚举，监听容器 22 端口，但禁用了登录认证；网站运行在 80 端口。

## 健康检查

```bash
docker ps --filter name=bike-lab
docker inspect --format '{{json .State.Health}}' bike-lab
curl -i http://127.0.0.1:8080/healthz
```

正常响应示例：

```json
{"status":"ok","services":{"web":"ok","ssh":"ok"}}
```

Dockerfile 的 `HEALTHCHECK` 每 20 秒检测 HTTP /healthz 和 SSH 握手。如果某一服务失效，容器健康状态变成 `unhealthy`。注意：原生 Docker 不会因为 `unhealthy` 自动重启容器；`--restart` 主要处理容器进程退出。

## 行为核对

```bash
curl -i http://127.0.0.1:8080/
curl -s -X POST --data-urlencode 'email=test@example.com' http://127.0.0.1:8080/
curl -i -X POST --data-urlencode 'email={{7*7}}' http://127.0.0.1:8080/
```

PDF 的 `POST /`、`email` 参数与 Handlebars 模板注入已复现。`/root/flag.txt` 是示例 flag，不是原题真实 flag。页面风格相近，非原站点像素级复刻。Node.js / Handlebars 故意使用可兼容旧链路的组合，含已知安全缺陷。请勿升级 Handlebars 后仍期待漏洞成立。

## 停止、删除

```bash
docker rm -f bike-lab
```

## 验证完整 SSTI 漏洞链

此靶机**故意**使用 Handlebars 4.1.2，并把 `POST /` 的 `email` 参数直接拼入待编译的模板源码（`server.js` 中的 `render()`）。因此它不只是回显 `{{...}}`，而是会把攻击者的 Handlebars 语法当模板执行。

GitHub Actions 使用独立的 Python 攻击端容器，通过仅供本次 CI 使用的内部 Docker 网络访问靶机；测试端不挂载靶机文件系统，也不使用 Docker socket。CI 会从当前 Challenge 对应的 Flag seed 读取预期答案，并实际通过 HTTP 请求走完 SSTI 到 `/root/flag.txt` 的路径。

本地验证时，启动靶机并将端口绑定到回环地址后执行：

```bash
EXPECTED_FLAG='TTP{your_local_flag}' python3 verify_ssti.py --url http://127.0.0.1:8080
```

测试脚本覆盖：

1. 正常邮箱原样回显；
2. `{{7*7}}` 触发 Handlebars 模板解析错误；
3. 按 PDF 中的 `constructor` / `process.mainModule` 链访问 `child_process`，验证 `id -un` 返回 `root`；
4. 通过同一链读取 `/root/flag.txt` 中的**本地模拟 Flag**。

只有上述四项全部通过，才算验证了 PDF 中的完整 SSTI 利用链。脚本默认只接受 `localhost` 或 `127.0.0.1`；只有设置 `ALLOW_INTERNAL_TARGET=1` 时才接受 CI 专用的 `bike-target:80` 内部网络地址。不要把漏洞服务暴露到公网。

> 环境说明：此项目的源码与测试脚本已完成静态语法检查；若构建环境未提供 Docker / npm 网络访问，则需要在实际构建镜像并运行后执行上述端到端验证。`HEALTHCHECK` 仅监测 HTTP/SSH 服务可用性，不主动执行漏洞利用验证。

## CI 与 Flag 发布

- `.github/workflows/bike.yml`：构建镜像、等待 Web/SSH 健康检查，并启动独立攻击端容器，通过真实 SSTI 请求读取目标 Flag。CI 不通过 `docker exec` 进入靶机，也不挂载目标文件系统。
- `scripts/generate_bike_release.py` 与 `.github/workflows/bike-release.yml`：按版本生成随机 80-bit Flag，保存 Manifest，并同步 `flags/root.txt` 与 Challenge 答案。同一版本重跑会复用原 Flag，新版本才轮换。
- 普通构建/健康检查与完整 Web 攻击路径分开记录；完整路径只有独立攻击端实际取回正确 Flag 才算通过。
