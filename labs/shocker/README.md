# Shocker — 原版 GNU Bash 4.3 / Apache CGI 复现（测试分支）

> 不是 HTB 官方镜像。**真实 Bash 4.3 / CGI / sudo 漏洞链 Docker CI 已通过；尚未完成正式 Worker 端到端验收，未合并也未发布。**

## 真实利用链

1. 端口扫描发现 Apache HTTP 80 与 SSH 2222。初始页面是很简单的虫子静态图形，不告诉玩家漏洞位置；原版 HTB 图片没有公开可复用的授权素材，所以首页图形是简化重制。
2. 枚举隐藏的 `/cgi-bin/` 并继续扫描 `.sh` 扩展名找到 `user.sh`。该文件通过 **Apache 原生 CGI** 执行系统监控的 `uptime`，不伪造 CGI 响应。
3. 真实、未经 Shellshock 修补的 GNU Bash **4.3 原始发布版**读取 Apache CGI 的请求头环境变量时，触发 **CVE-2014-6271**，并以真实 Unix 用户 `shelly`（UID 1001）执行命令。
4. 取得 `/home/shelly/user.txt` 后，利用真实 `sudoers` 允许 `shelly` 无需密码运行 `/usr/bin/perl` 的配置取得 Root，再读取 `/root/root.txt`。

## 上游来源

- GNU Bash 4.3 官方发布：https://lists.gnu.org/archive/html/info-gnu/2014-02/msg00010.html
- 官方源码：https://ftp.gnu.org/gnu/bash/bash-4.3.tar.gz
- SHA-256：`afc687a28e0e24dc21b988fa159ff9dbcf6b7caa92ade8645cc6d5605cd024d4`（Gentoo 历史归档验证）。
- Shocker Writeup：https://blog.d3vyce.fr/writeup-ctf/writeup-shocker-htb/
- 第二份：https://joeylipton.ca/2022/05/01/HTB-Shocker.html
- GNU Bash 的 GPL 许可证 `COPYING` 从上游编译阶段复制到最终镜像。

## 轻量镜像

多阶段构建：第一阶段 Alpine 3.15 用 build-base 编译真 Bash 4.3；第二阶段仅拷贝旧 Bash 二进制、保留 Apache、OpenSSH、sudo、Perl 等服务。不加入 GCC、编译器、MySQL、PHP、Java。**CI 实测镜像 16.4 MiB、运行内存 4.1 MiB、7 PIDs**（快照；非峰值/并发测试）。CI 运行限额 96 MiB、96 PIDs，真实 Apache CGI 和 sudo Perl Root 测试通过。验收日志：https://github.com/10010100111000/AttackBoxModule/actions/runs/44955028484

原题 Ubuntu 16.04、Apache2 2.4.18、SSH 2222，当前开发采用 Alpine 3.15 并保留端口、真实 CGI 行为和 Perl sudo 提权，不伪造软件版本指纹。初始页面为仅外观重制，不声称是官方图形。

## 构建

在仓库根目录：

```bash
docker build -f labs/shocker/Dockerfile -t ttp-shocker:dev labs/shocker
docker run --rm -d --name shocker --network none ttp-shocker:dev
docker inspect -f '{{.State.Health.Status}}' shocker
```

实际玩家访问只能走私有靶机网络，不能暴露真实漏洞或 SSH 到公网。端到端测试通过独立的 Python 攻击容器和真实 sudo 检查；测试脚本不会进入运行镜像。

静态演示 Flags：`/home/shelly/user.txt` 与 `/root/root.txt`。生产时由 Worker 为每实例注入 `SHOCKER_STATIC_USER_FLAG`、`SHOCKER_STATIC_ROOT_FLAG` 和 `SHOCKER_REQUIRE_PRIVATE_FLAGS=1`，正式答案不写入公开仓库。
