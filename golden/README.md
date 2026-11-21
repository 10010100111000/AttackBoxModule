# AttackBox 金盘

金盘提供 MATE 桌面、Chromium、TigerVNC，以及 Web、AD/内网学习工具。平台 Worker 从金盘创建每位学员的独立 Btrfs 快照。

## 构建来源

基础系统制作方式改编自 Parrot 官方 [parrot-chroot-build](https://gitlab.com/parrotsec/build/parrot-chroot-build)，参考提交 [`306a445874d58c836ac7d7a04ec0bc0b2c2547a5`](https://gitlab.com/parrotsec/build/parrot-chroot-build/-/tree/306a445874d58c836ac7d7a04ec0bc0b2c2547a5)。通过 debootstrap 从已签名的 `echo` 软件仓库创建 amd64 根文件系统，再安装官方完整 MATE 桌面。

构建主机使用 Ubuntu 的 Debian suite 脚本，显式指定 Parrot 的 suite、镜像源及校验过的归档密钥。归档密钥 SHA-256 固定在 `build.sh` 中；密钥更新时核验官方来源并更新校验值。

## 维护软件

软件策略分为三份清单：

| 文件 | 用途 |
| --- | --- |
| `desktop-packages.txt` | 官方 `mate-desktop-environment` 元包，连同 Depends 和 Recommends 安装完整桌面 |
| `packages.txt` | 平台适配、Chromium、HTB 外观与已确认的教学工具，APT 安装其依赖 |
| `remove-packages.txt` | 明确卸载的软件；APT 模拟结果出现清单之外的级联删除时停止构建 |

`install-packages.sh` 安装软件、更新系统并执行移除策略。软件卸载使用 APT，移除范围由清单控制；实际版本与安装大小记录在 `packages.tsv`，三份策略清单一同保存在金盘的 `/usr/share/attackbox/`。

远程桌面采用无音频 VNC 配置，移除音频服务、音量控制器、英文语音识别模型、电池管理、离线桌面用户手册和额外 MATE 壁纸集。HTB／Parrot 外观、常用桌面操作、命令行手册和已确认的教学工具保留。

桌面组件由官方元包维护。项目保留发行版的 Shell 和应用用户模板，HTB 外观字段来自 Parrot 软件包。`attackbox.layout` 维护已选定的 BriskMenu 搜索菜单、顶部启动器和底部任务栏，`mate-defaults.ini` 维护平台需要的运行设置。

`parrot-menu` 提供官方安全工具分类，`ShowInstallableLaunchers=false` 使菜单按实际安装的软件生成入口。软件安装及移除后调用发行版的 `update-launchers` 更新分类；用户模板中的启动器也参与统一处理，未安装的用户应用通过 `TryExec` 自动隐藏。

默认应用由 `desktop_defaults.py` 统一配置：网页使用 Chromium，目录使用 Caja，文本使用 Geany，图片使用 EOM，压缩包使用 Engrampa。截图、文件搜索、计算器、通知和 SMB／SFTP 浏览由完整桌面提供；中文字体、主题引擎和浏览器相关配置由平台适配清单提供。

教学工具按管理员确认的清单安装：Burp、Wireshark、Geany、FreeRDP；ffuf、Gobuster、dirsearch、wfuzz、dirb、sqlmap、WPScan、Nikto；Nmap、Masscan、协议客户端与抓包工具；Metasploit、Impacket、NetExec、evil-winrm、SMB 枚举、Windows/PowerShell 载荷；Chisel、Proxychains、Redis/MySQL/PostgreSQL 客户端；密码分析工具与完整字典库。Python、C/C++、Java、Node/npm 和 Go 编译环境保留。

MATE 保留窗口管理、面板、终端和文件管理器，关闭合成、动画及会话自动恢复。本地图片显示缩略图，终端保留 10,000 行滚动记录，`Ctrl+Alt+T` 打开终端。运行设置由 `mate-defaults.ini` 维护，并对照已安装的 GSettings schema 校验路径、键名及值。TigerVNC 服务端和剪贴板工具用于平台 GUI；`vncconfig` 菜单入口隐藏，后台同步功能保留。

构建完成前验收桌面元包和教学工具均已安装、移除清单中的软件均未安装，以及语言环境、主题资源和关键程序可用。

构建时生成并验证 `en_US.UTF-8`、`zh_CN.UTF-8`，默认使用英文界面。用户模板继承发行版的 `/etc/skel`，`desktop_defaults.py` 配置默认应用、桌面入口和标准目录，目录语言标记固定为 `en_US`。桌面主题来自系统 dconf，个人设置保存在各自的用户目录。

`chromium-policy.json` 管理浏览器后台行为和扩展安装，默认安装 FoxyProxy、Wappalyzer、Cookie-Editor。浏览器以 `box` 用户运行，保持自身安全沙箱。可以通过 `chrome://policy` 检查策略，首次启动需要联网获取扩展。

Worker 桌面通过切换用户启动，没有 PAM 登录来解锁系统密钥环。`chromium-flags.sh` 通过 Debian 浏览器的 `/etc/chromium.d/attackbox` 入口统一选择 `basic` 本地凭据存储，浏览器状态随学员的沙箱快照保存与释放；该存储不使用系统密钥环加密。保存密码功能由托管策略关闭。

`bin/burpsuite` 和对应桌面入口启动已安装的 Burp，并关闭其自动更新提醒。Burp 在学员打开时启动。使用外部浏览器抓包时，代理地址为 `127.0.0.1:8080`；构建阶段以 `box` 身份启动 Burp，按仓库所有者授权接受 Community 条款，由 Burp 生成 CA，并保存其真实 CA 配置和条款状态。每个金盘版本的实例共用该版本 CA，浏览器 NSS 信任库预先导入对应证书；该 CA 用于金盘内的实验浏览器。构建机器标识和窗口状态不进入用户模板。

`burp-user-config.json` 将启动时拦截设为关闭，并关闭匿名反馈；学员可在 Burp 中开启拦截。CA 初始化和验证代码在 `burp_ca.py`，不会安装为学员的常驻服务。

`install-packages.sh` 负责软件安装与移除，`configure.sh` 负责账号、sudo、语言和桌面默认配置；`build.sh` 负责基础系统引导、隔离挂载、清理和锁定子卷。账号由系统工具维护，`box` 固定为 `1001:1013`。金盘内的 machine-id 为空；平台接入时需要在每个实例初始化阶段生成独立标识。

`cleanup.py` 在根文件系统卸载后清理构建临时文件、APT 下载与索引、日志、用户缓存、回收站、历史记录和旧会话，并移除其他桌面及未安装 Neovim 的残留配置。Burp CA、NSS 证书库、字体／图标缓存、GSettings schema 和 dpkg 数据库保留。`cleanup-report.json` 记录实际移除包的原安装大小及清掉的文件内容大小；压缩产物体积以 Release 分卷为准。

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
| `cleanup-report.json` | 移除的软件包、安装大小估计与清理文件内容的字节数 |

软件包来自持续更新的 Parrot 仓库。manifest 记录教材仓库提交及参考的上游构建提交，包清单记录实际安装版本。安装端按 manifest 顺序验证并接收分卷。

工作流验证源子卷与回读子卷的结构、只读属性、locale、文件 capabilities 和安装清单，并在临时快照中运行 `check-desktop.sh`：以 `box` 用户启动 TigerVNC、MATE 和 Chromium，验证 VNC 握手、浏览器 JavaScript 及三个扩展的安装。`desktop_check.py` 按安装的 applet 注册信息检查布局中的 IID、执行文件、启动器和主题资源；桌面启动期间通过 X11 监测错误对话框，先注入并关闭一个测试对话框确认探测器能拒绝它，再持续监测真实桌面；检测到面板或 applet 弹窗时验收失败，窗口信息写入测试日志。`desktop_smoke.py` 使用原生 MateMenu 库验证安全工具分类和可见浏览器入口，再在同一会话验证默认打开方式、真实截图、图片和文本打开、终端执行、文本剪贴板、ZIP 往返与回收站操作。验收还会重新启动 Burp、核对 CA、通过本地 HTTPS 测试服务验证 TLS 抓包，并确认 Chromium 正常加载被代理的 HTTPS 页面。测试保留证书校验和浏览器安全沙箱。日常文件操作的测试数据放在学员主目录。测试在独立挂载和 PID 命名空间运行，结束后删除测试快照。

窗口观察器从 X11 根窗口读取客户端 ID，再逐个读取属性；查询期间已经关闭的客户端从本次快照中略过，显示连接错误和仍存在的错误弹窗会使验收失败。

桌面验收会拒绝启动期间出现的密钥环密码对话框。失败时输出具体阶段、浏览器页面信息和 X11 窗口快照，再清理测试子卷，便于定位失败原因。

真实 Worker 的权限、网络、GUI 网关和释放验收属于平台接入步骤；CI 的桌面测试用于确认金盘本身可以运行。

## 本地运行

Linux amd64 构建主机需要 root、Btrfs、debootstrap、curl、GnuPG、Python 3、zstd，以及可用的挂载命名空间。构建期间需要访问 Parrot 软件仓库。

```bash
python3 -m unittest discover -s golden/tests
sudo bash golden/build.sh --target /mnt/btrfs/base_rootfs
sudo bash golden/check.sh /mnt/btrfs/base_rootfs
sudo bash golden/check-desktop.sh /mnt/btrfs/base_rootfs
```
