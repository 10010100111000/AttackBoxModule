# Nibbles — 原版 Nibbleblog 4.0.3（测试中）

> 实现分支：`test/nibbles-authentic-small`。**已通过 Docker CI 的真实漏洞和重置测试，但尚未在正式 Worker 验收，不发布。** 不是 HTB 官方镜像。

## 为什么选择这台

上一台 Pebbles 同时运行 MySQL、ZoneMinder 和 Tomcat，资源占用较高。Nibbles 原题使用真正的 **Nibbleblog 4.0.3**，它通过 XML 文件存储信息，完全不需要数据库服务器或 Java。我们固定的是上游 2014-04-01 发布的原始 Git Commit，使用它自己的 PHP 前端、安装程序和 My Image 插件，而不是编写自制漏洞页面。

### 玩家真实发现路径

1. 扫描实际目标：22/tcp SSH 与 80/tcp Apache；首页仅有 `Hello world!`，HTML 源码中留有 `/nibbleblog/` 注释。
2. 访问该目录后枚举真正 Nibbleblog CMS 的 README、config.xml、users.xml、admin.php；根据原始信息识别版本与用户。
3. 经 CMS 原生登录页面进入管理界面，安装 / 配置 My Image 插件。
4. 插件真实的 `admin/controllers/plugins/config.bit` 使用 `move_uploaded_file()`，未限制文件的可执行扩展名。按照 CVE-2015-6967 能上传并运行 PHP 文件，PHP 子进程作为 `nibbler`（UID 1001）运行。
5. 取得 `/home/nibbler/user.txt`，发现 `personal.zip` 与 sudoers 对 `monitor.sh` 的特殊许可；解压后编辑具有写权限的监控脚本，用真正的 sudo 执行获得 UID 0，再取得 `/root/root.txt`。

原题首页及 `personal.zip` 的确切原始内容未公开，所以这两部分是**可说明的行为重建**，不是偷换原版漏洞或模拟提权。用户后台和不安全上传 PHP 处理代码来自真正的上游软件，未编写替代接口。

## 真实软件与许可证

- 上游发布提交：https://github.com/dignajar/nibbleblog/commit/6fe138276e82ed604bb35a960327a4ac0b485097
- 官方 SourceForge 归档：https://sourceforge.net/projects/nibbleblog/files/v4.0/nibbleblog-v4.0.3.zip/download
- 漏洞公告：https://github.com/advisories/GHSA-jc49-pxch-59wj
- 原题 Writeup：https://cornfield.sh/htb-nibbles/
- 第二份 Writeup：https://trophyroom.thomaslaurenson.com/hackthebox/nibbles/

原版 `LICENSE.txt` 和 `COPYRIGHT.txt` 均保留在镜像中。仅上游 4.0.3 提交中遗留的 README 版本元数据从 “Beta on Github” 修正为同一版本常量所代表的 4.0.3；未修改 PHP 漏洞代码。原题采用 Ubuntu 16.04，本复现为减小体积使用 Alpine 3.15/Apache/PHP 7.4，**OS 与 PHP 版本差异公开标注**，不会伪造版本指纹。

## Docker 工程

在仓库根目录运行：

```bash
docker build -f labs/nibbles/Dockerfile -t ttp-nibbles:dev labs/nibbles
docker run --rm -d --name nibbles --network none --memory 160m --pids-limit 128 ttp-nibbles:dev
docker inspect -f '{{.State.Health.Status}}' nibbles
```

上述 `--network none` 仅供镜像/健康检查。CI 使用隔离私有 Docker 桥与独立的攻击容器检查 HTTP 枚举、真实插件上传、系统用户/Root 及实例重置。任何故意有漏洞的服务禁止公网映射。

静态 Flag（仓库内仅演示值）：普通权限 `/home/nibbler/user.txt`；Root 只读 `/root/root.txt`。正式平台实例应通过现有 Worker 运行环境注入 `NIBBLES_STATIC_USER_FLAG`、`NIBBLES_STATIC_ROOT_FLAG`、`NIBBLES_REQUIRE_PRIVATE_FLAGS=1`，并配置同样的服务端静态判题答案，绝不将正式答案提交到公共 Git。

## 占用目标与验收

- **实测镜像 25.0 MiB，CI 快照内存 17.2 MiB、8 PIDs**；CI 限制 160 MiB 和 128 PIDs，单 Docker 实例。数据为一次运行快照，不是并发峰值。
- 完整构建和原版 CMS 上传 → native sudo Root → 两枚静态 Flag → 清除状态：**CI 通过**。https://github.com/10010100111000/AttackBoxModule/actions/runs/44954697830
- 不安装 MySQL、MariaDB、Java/Tomcat、Python 或 GUI。
- CI 必须测试原生 CMS 版本及 PHP 登录、My Image 上传、以 UID 1001 执行、sudo UID 0、两枚静态 Flag、停止删除再建的重置流程。
- 不将测试用 Python 或 Exploit 脚本复制到最终运行镜像。
- 在 CI 验证结束之前，不作“已完成”的宣传，不合并主分支、不自动发布。
