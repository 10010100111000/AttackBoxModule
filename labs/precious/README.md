# Precious — Ruby PDFKit command injection

**范围：HTB Precious 的 Web 阶段重建。** 本项目保留真实 PDFKit 0.8.6 与原生 wkhtmltopdf，不模拟命令执行，也不包含原题后续的 SSH 凭据复用、YAML 反序列化或 Linux Root 提权。

## 技术组成

- Ruby 3.1
- Sinatra 2.2.4
- PDFKit 0.8.6
- 原生 wkhtmltopdf
- Debian Bookworm slim
- 非 root 的 `ruby` 服务账户
- Web Flag：`/home/ruby/user.txt`

PDFKit 0.8.6 的 `PDFKit#command` 会把 URL source 原样拼入待执行命令；上游源码明确说明 source 不做 shell escaping。应用将用户提交的 URL 直接传给真实的 `PDFKit.new`，因此保留 CVE-2022-25765 的实际命令注入路径。

## 构建与启动

```sh
docker build -t ttp-precious:local -f labs/precious/Dockerfile labs/precious

docker run --rm -d --name precious-lab \
  --memory 700m --cpus 1 --pids-limit 150 \
  --security-opt no-new-privileges \
  -p 127.0.0.1:8080:8080 \
  ttp-precious:local

docker inspect -f '{{.State.Health.Status}}' precious-lab
curl -i http://127.0.0.1:8080/
```

默认 Flag 来自 `labs/precious/flags/user.txt`。发布时由版本化 Flag 工作流生成，并将目标文件与 Challenge 答案同步。

## CI 范围

普通 CI 只检查：

- Docker 镜像能否构建；
- 容器能否启动并通过 Healthcheck；
- PDFKit 实际加载版本是否为 0.8.6；
- 首页是否正常响应；
- 正常的内部 HTML 页面是否能被转换为有效 PDF；
- 镜像大小及运行时资源快照。

CI 不执行命令注入、读取 Flag、反向连接或其他自动攻击流程。正常 PDF 转换通过，只代表普通业务功能正常，不代表漏洞利用链已经人工验收。

## Flag 发布

使用 `.github/workflows/precious-release.yml` 手动发布指定版本：

- 首次发布某版本时生成随机 80-bit Flag；
- 保存到 `labs/precious/flags/releases/<version>.json`；
- 同步 `labs/precious/flags/user.txt` 与 `challenges/integrated/precious/Precious.md`；
- 重复运行同一版本复用 Manifest 中的 Flag；
- 使用新版本才会生成新 Flag。

## 来源

- HTB：<https://www.hackthebox.com/machines/precious>
- 0xdf 原版 Writeup：<https://0xdf.gitlab.io/2023/05/20/htb-precious.html>
- PDFKit 0.8.6 上游：<https://github.com/pdfkit/pdfkit/tree/v0.8.6>
- CVE-2022-25765：<https://nvd.nist.gov/vuln/detail/CVE-2022-25765>

原题的 Web 站点源代码未公开；本项目重建可观察的 URL 转 PDF 页面和真实漏洞组件，不声称复制原站私有源码。
