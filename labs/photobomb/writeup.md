# Photobomb — Writeup

## 目标与环境

目标是复现退役 HTB Photobomb 的公开攻击路径。原始 Sinatra 应用源码没有公开仓库，因此 Web 应用按公开页面、JavaScript、请求参数和 Writeup 中记录的行为独立重建；漏洞仍由真实 Ruby/Sinatra、shell、ImageMagick、sudo 和系统脚本执行，不使用模拟命令接口。

## 1. 侦察与正常浏览

先枚举目标开放服务，识别 HTTP 与 SSH。浏览首页，页面介绍在线照片打印服务。首页没有直接展示管理功能，继续检查静态 JavaScript 文件及页面链接。

JavaScript 中保留了技术支持入口的凭据线索。使用发现的凭据访问受 HTTP Basic Authentication 保护的 /printer 页面。

## 2. 观察正常图片转换

打印页面允许选择照片、输出格式和尺寸。先提交正常请求，确认服务器会执行 ImageMagick convert，并返回实际生成的图片。

继续检查 Sinatra 的 POST /printer 处理逻辑。应用对 filetype 使用前缀匹配校验，但随后将该值直接拼接进传递给 system() 的命令字符串。校验只确认字符串以 png 或 jpg 开头，并没有限制后续 shell 元字符。

## 3. 命令注入与 wizard

构造以合法格式前缀开头、后续包含 shell 命令分隔符的 filetype 值。请求仍经过真实 /printer 路由，Sinatra 最终调用 system()，由 shell 解释拼接后的命令。

命令以 Web 应用运行账户 wizard 的身份执行。读取 /home/wizard/user.txt，取得 User Flag。

## 4. 检查 sudo 维护权限

以 wizard 身份检查 sudo 授权。该账户可以免密执行 /opt/cleanup.sh，并且 sudoers 规则允许设置环境变量。

检查脚本内容：它切换到应用目录并调用 find，但没有使用 find 的绝对路径。由于应用目录由 wizard 写入，且 PATH 可由调用者控制，脚本会从该目录优先解析 find。

## 5. PATH 劫持取得 root

在可写目录中创建同名 find 程序，并通过 sudo 传入将该目录置于 PATH 首位的环境。执行原本授权的 /opt/cleanup.sh 时，root 上下文会调用攻击者控制的 find。

验证进程身份为 UID 0，并读取 /root/root.txt 中的 Root Flag。

## 根因与修复建议

- 不要把未经严格约束的用户输入拼接到 shell 命令。优先使用 Ruby 的参数数组形式调用子进程，避免 shell 解析；对格式和尺寸使用完整匹配与白名单。
- 对外部程序参数分别校验，不能用“合法前缀”代替完整输入验证。
- sudo 维护脚本应使用外部程序的绝对路径，并清理继承的环境变量。
- 不要让高权限脚本在普通用户可写目录中执行命令解析；对 sudoers 的 SETENV 授权应保持最小化。

## 复现边界

- Sinatra 路由和页面行为是根据公开 Writeup 重建，并非声称持有 HTB 原始私有源码。
- ImageMagick convert 是真实图像处理程序；命令注入发生在真实 system() 调用。
- sudo、PATH 解析、find 和 Flag 文件均使用真实 Linux 组件。
