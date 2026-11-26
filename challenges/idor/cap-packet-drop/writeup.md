# Packet Drop — Writeup

## 目标

通过 Cap 风格安全仪表板中的 IDOR 下载其他用户的 PCAP，分析真实 FTP 流量并复用其中的凭据，取得用户级 Flag。

## 1. 侦察 Web 仪表板

访问仪表板，确认页面提供 Security Snapshot 功能。触发一次正常快照，观察浏览器跳转到类似 `/data/<id>` 的页面，并留意下载链接 `/download/<id>`。

这里的数字 ID 是访问对象的直接引用。需要确认服务端是否将对象与当前用户或会话绑定。

## 2. 验证 IDOR

将快照编号替换为其他有效编号，访问对应的数据页面和下载端点。应用没有执行所有权或会话授权检查，因此未登录访客也可以读取其他用户的 PCAP。

## 3. 分析 PCAP

下载历史快照，使用 Wireshark、tshark 或 tcpdump 检查 FTP 控制连接。FTP 登录使用明文控制命令，因此捕获内容中可以看到用户名和密码。

关注 `USER` 与 `PASS` 命令，并记录发现的凭据。

## 4. 验证凭据复用

使用发现的凭据连接目标 FTP 服务，确认登录成功。浏览用户目录并下载 `user.txt`，取得本题 Flag。

## 漏洞链总结

1. 发现数字编号的网络快照。
2. 通过 IDOR 访问其他用户的快照。
3. 下载并分析真实 PCAP。
4. 从 FTP 控制流中恢复明文凭据。
5. 将凭据复用于 FTP 服务。
6. 下载并提交用户 Flag。

## 关键实现位置

- `labs/cap/app.py`：`/data/<capture_id>` 与 `/download/<capture_id>` 未验证对象归属。
- `labs/cap/Dockerfile`：构建阶段通过真实 vsftpd 登录会话生成种子 PCAP。
- `labs/cap/tests/attack_path.py`：独立玩家通过 HTTP、PCAP 分析和 FTP 验证完整路径。

## 参考资料

- HTB Cap：https://www.hackthebox.com/machines/cap
- 0xdf Writeup：https://0xdf.gitlab.io/2021/10/02/htb-cap.html
- ch3sh Writeup：https://ch3sh.github.io/hackthebox/HTB-Cap/

本题复现公开证据中的 Web IDOR、真实 FTP PCAP 和凭据复用路径；原始 HTB Flask 源码未公开，因此 Web 应用属于基于观察行为的重建。
