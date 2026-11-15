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

在仅绑定本机回环地址的靶机启动后执行：

```bash
python3 verify_ssti.py
```

测试脚本覆盖：

1. 正常邮箱原样回显；
2. `{{7*7}}` 触发 Handlebars 模板解析错误；
3. 按 PDF 中的 `constructor` / `process.mainModule` 链访问 `child_process`，验证 `id -un` 返回 `root`；
4. 通过同一链读取 `/root/flag.txt` 中的**本地模拟 Flag**。

只有上述四项全部通过，才算验证了 PDF 中的完整 SSTI 利用链。该脚本仅接受 `localhost` 或 `127.0.0.1` 地址；不要把漏洞服务暴露到公网。

> 环境说明：此项目的源码与测试脚本已完成静态语法检查；若构建环境未提供 Docker / npm 网络访问，则需要在实际构建镜像并运行后执行上述端到端验证。`HEALTHCHECK` 仅监测 HTTP/SSH 服务可用性，不主动执行漏洞利用验证。
