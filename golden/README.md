# AttackBox 金盘

金盘提供 MATE 桌面、Firefox、TigerVNC，以及 Web、AD/内网学习工具。平台 Worker 从金盘创建每位学员的独立 Btrfs 快照。

## 构建来源

基础系统制作方式改编自 Parrot 官方 [parrot-chroot-build](https://gitlab.com/parrotsec/build/parrot-chroot-build)，参考提交 [`306a445874d58c836ac7d7a04ec0bc0b2c2547a5`](https://gitlab.com/parrotsec/build/parrot-chroot-build/-/tree/306a445874d58c836ac7d7a04ec0bc0b2c2547a5)。通过 debootstrap 从已签名的 `echo` 软件仓库生成 amd64 最小系统。

构建主机使用 Ubuntu 的 Debian suite 脚本，显式指定 Parrot 的 suite、镜像源及校验过的归档密钥。归档密钥 SHA-256 固定在 `build.sh` 中；密钥更新时核验官方来源并更新校验值。

## 维护软件

`packages.txt` 是唯一的安装清单，每行一个 APT 软件包。全部条目都必须成功安装。APT 自动解析依赖，以 `--no-install-recommends` 安装。

桌面按 MATE 组件安装，HTB 主题和系统默认设置来自 Parrot 软件包。清单包含 Firefox、FoxyProxy、中文字体、TigerVNC 工具、SSH 客户端、编译工具、SecLists、常用枚举和网络客户端。

Burp、Caido、Metasploit、BloodHound、Remmina、Go、Node、Python、Wireshark 和 Hashcat 均包含在默认清单中。BloodHound 的 Neo4j/PostgreSQL、Metasploit 的数据库与编译依赖、Hashcat 的 CPU OpenCL 运行时会增加体积；具体安装版本与大小记录在发布产物 `packages.tsv` 中。Java 使用 `default-jre`，工具所需的特定 Java 版本由 APT 管理。theHarvester 的网页采集功能会引入 Chromium。

`configure.sh` 负责账号、sudo、语言和桌面默认配置；`build.sh` 负责引导、隔离挂载、清理和锁定子卷。账号由系统工具维护，`box` 固定为 `1001:1013`。金盘内的 machine-id 为空，部署端在每个实例初始化时分配独立标识。

## GitHub Actions

在 **Actions → Build golden image → Run workflow** 中填写三段版本号，例如 `1.0.0`。

- `publish=false`：构建、导出、SHA-256 检查和 Btrfs 回读通过后，将完整产物保存为 Actions artifact，保留三天。
- `publish=true`：验收后上传到草稿 Release，全部上传成功后发布为 `golden-v1.0.0`。已发布版本使用新的版本号更新。

工作流由手动操作触发。靶机镜像工作流只监听 `labs/` 及自身配置的变更。

每个产物包含：

| 文件 | 用途 |
| --- | --- |
| `attackbox-golden-manifest.json` | 格式版本、金盘版本、来源及有序分卷列表 |
| `attackbox-golden.btrfs.zst.part-*` | 每卷最多 1900 MiB 的压缩 Btrfs 数据流 |
| `attackbox-golden.sha256` | 分卷校验值 |
| `packages.tsv` | 实际安装的软件包、版本及安装大小（KiB） |

软件包来自持续更新的 Parrot 仓库。manifest 记录教材仓库提交，包清单记录实际安装版本。安装端按 manifest 顺序验证并接收分卷。

当前工作流验证源子卷与导出后接收的子卷结构、只读属性及离线 CLI。真实 Worker 的沙箱创建、GUI、能力和释放验收属于平台接入步骤，部署前必须完成。

## 本地运行

Linux amd64 构建主机需要 root、Btrfs、debootstrap、curl、GnuPG、Python 3、zstd，以及可用的挂载命名空间。

```bash
python3 -m unittest discover -s golden/tests
sudo bash golden/build.sh --target /mnt/btrfs/base_rootfs
sudo bash golden/check.sh /mnt/btrfs/base_rootfs
```
