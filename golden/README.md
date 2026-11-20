# AttackBox 金盘

金盘提供 MATE 桌面、Chromium、TigerVNC，以及 Web、AD/内网学习工具。平台 Worker 从金盘创建每位学员的独立 Btrfs 快照。

## 构建来源

基础系统制作方式改编自 Parrot 官方 [parrot-chroot-build](https://gitlab.com/parrotsec/build/parrot-chroot-build)，参考提交 [`306a445874d58c836ac7d7a04ec0bc0b2c2547a5`](https://gitlab.com/parrotsec/build/parrot-chroot-build/-/tree/306a445874d58c836ac7d7a04ec0bc0b2c2547a5)。通过 debootstrap 从已签名的 `echo` 软件仓库生成 amd64 最小系统。

构建主机使用 Ubuntu 的 Debian suite 脚本，显式指定 Parrot 的 suite、镜像源及校验过的归档密钥。归档密钥 SHA-256 固定在 `build.sh` 中；密钥更新时核验官方来源并更新校验值。

## 维护软件

`packages.txt` 是唯一的安装清单，每行一个 APT 软件包。全部条目都必须成功安装。APT 自动解析依赖，以 `--no-install-recommends` 安装。

桌面按 MATE 组件安装，HTB 主题、壁纸和终端配色按选定外观字段提取自 Parrot 软件包，GTK2 的 Murrine、Pixmap 主题引擎一并安装。面板由 `attackbox.layout` 统一定义，包含 BriskMenu 搜索菜单、顶部启动器和底部任务栏。`mate-applet-brisk-menu` 与布局一起维护。清单包含 Chromium、中文字体、TigerVNC、FreeRDP、SSH 客户端、编译工具、SecLists、常用枚举和网络客户端。

日常桌面功能也明确列入清单：`mate-utils` 提供截图和文件搜索，`eom` 查看图片，`mate-calc` 提供计算器，`gvfs-backends` 为 Caja 提供 SMB／SFTP 浏览，`xclip` 提供命令行剪贴板访问。`desktop_defaults.py` 统一配置默认应用：网页使用 Chromium，目录使用 Caja，文本使用 Geany，图片使用 EOM，压缩包使用 Engrampa。

可选工具按管理员确认的清单安装：Burp、Wireshark、Geany、FreeRDP；ffuf、Gobuster、dirsearch、wfuzz、dirb、sqlmap、WPScan、Nikto；Nmap、Masscan、协议客户端与抓包工具；Metasploit、Impacket、NetExec、evil-winrm、SMB 枚举、Windows/PowerShell 载荷；Chisel、Proxychains、Redis/MySQL/PostgreSQL 客户端；密码分析工具与完整字典库。Python、C/C++、Java、Node/npm 和 Go 编译环境保留。

MATE 保留窗口管理、面板、终端和文件管理器，关闭合成、动画及会话自动恢复。本地图片显示缩略图，终端保留 10,000 行滚动记录，`Ctrl+Alt+T` 打开终端。运行设置由 `mate-defaults.ini` 维护，并对照已安装的 GSettings schema 校验路径、键名及值。TigerVNC 服务端和剪贴板工具用于平台 GUI；`vncconfig` 菜单入口隐藏，后台同步功能保留。

软件和依赖的实际版本及大小记录在 `packages.tsv` 中。从最小系统按清单安装显式桌面组件，依赖由 APT 解析；构建完成前执行全系统升级，验收安装清单和语言环境。

构建时生成并验证 `en_US.UTF-8`、`zh_CN.UTF-8`，默认使用英文界面。`skel/` 维护 Bash 的用户模板，用户目录由它和 `desktop_defaults.py` 创建，标准目录语言标记固定为 `en_US`。桌面主题来自系统 dconf，个人设置保存在各自的用户目录。

`chromium-policy.json` 管理浏览器后台行为和扩展安装，默认安装 FoxyProxy、Wappalyzer、Cookie-Editor。浏览器以 `box` 用户运行，保持自身安全沙箱。可以通过 `chrome://policy` 检查策略，首次启动需要联网获取扩展。

`bin/burpsuite` 和对应桌面入口启动已安装的 Burp，并关闭其自动更新提醒。Burp 在学员打开时启动。使用外部浏览器抓包时，代理地址为 `127.0.0.1:8080`；构建阶段以 `box` 身份启动 Burp，按仓库所有者授权接受 Community 条款，由 Burp 生成 CA，并保存其真实 CA 配置和条款状态。每个金盘版本的实例共用该版本 CA，浏览器 NSS 信任库预先导入对应证书；该 CA 用于金盘内的实验浏览器。构建机器标识和窗口状态不进入用户模板。

`burp-user-config.json` 将启动时拦截设为关闭，并关闭匿名反馈；学员可在 Burp 中开启拦截。CA 初始化和验证代码在 `burp_ca.py`，不会安装为学员的常驻服务。

`configure.sh` 负责账号、sudo、语言和桌面默认配置；`build.sh` 负责基础系统引导、隔离挂载、清理和锁定子卷。账号由系统工具维护，`box` 固定为 `1001:1013`。金盘内的 machine-id 为空；平台接入时需要在每个实例初始化阶段生成独立标识。

## GitHub Actions

在 **Actions → Build golden image → Run workflow** 中填写三段版本号，例如 `1.0.0`。

- `publish=false`：构建、导出、SHA-256 检查和 Btrfs 回读通过后，将完整产物保存为草稿 Release，供管理员下载检查。
- `publish=true`：验收后上传到草稿 Release，全部上传成功后发布为 `golden-v1.0.0`。已发布版本使用新的版本号更新。

工作流由手动操作触发。靶机镜像工作流只监听 `labs/` 及自身配置的变更。

每个产物包含：

| 文件 | 用途 |
| --- | --- |
| `attackbox-golden-manifest.json` | 格式版本、金盘版本、来源及有序分卷列表 |
| `attackbox-golden.btrfs.zst.part-*` | 每卷最多 1900 MiB 的压缩 Btrfs 数据流 |
| `attackbox-golden.sha256` | 分卷校验值 |
| `packages.tsv` | 实际安装的软件包、版本及安装大小（KiB） |

软件包来自持续更新的 Parrot 仓库。manifest 记录教材仓库提交及参考的上游构建提交，包清单记录实际安装版本。安装端按 manifest 顺序验证并接收分卷。

工作流验证源子卷与回读子卷的结构、只读属性、locale、文件 capabilities 和安装清单，并在临时快照中运行 `check-desktop.sh`：以 `box` 用户启动 TigerVNC、MATE 和 Chromium，验证 VNC 握手、浏览器 JavaScript 及三个扩展的安装。`desktop_check.py` 按安装的 applet 注册信息检查布局中的 IID、执行文件、启动器和主题资源；桌面启动期间通过 X11 监测错误对话框，先注入并关闭一个测试对话框确认探测器能拒绝它，再持续监测真实桌面；检测到面板或 applet 弹窗时验收失败，窗口信息写入测试日志。`desktop_smoke.py` 在同一会话验证默认打开方式、真实截图、图片和文本打开、终端执行、文本剪贴板、ZIP 往返与回收站操作。验收还会重新启动 Burp、核对 CA、通过本地 HTTPS 测试服务验证 TLS 抓包，并确认 Chromium 正常加载被代理的 HTTPS 页面。测试保留证书校验和浏览器安全沙箱。测试在独立挂载和 PID 命名空间运行，结束后删除测试快照。

真实 Worker 的权限、网络、GUI 网关和释放验收属于平台接入步骤；CI 的桌面测试用于确认金盘本身可以运行。

## 本地运行

Linux amd64 构建主机需要 root、Btrfs、debootstrap、curl、GnuPG、Python 3、zstd，以及可用的挂载命名空间。构建期间需要访问 Parrot 软件仓库。

```bash
python3 -m unittest discover -s golden/tests
sudo bash golden/build.sh --target /mnt/btrfs/base_rootfs
sudo bash golden/check.sh /mnt/btrfs/base_rootfs
sudo bash golden/check-desktop.sh /mnt/btrfs/base_rootfs
```
