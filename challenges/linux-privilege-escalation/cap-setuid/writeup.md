# Root of Trust — Writeup

## 目标

完成 Cap 的完整利用路径：Web IDOR、PCAP 凭据泄露、FTP/SSH 凭据复用，以及 Python `cap_setuid` 权限提升。

## 1. 从 Web IDOR 取得 PCAP

访问安全仪表板并触发网络快照，观察 `/data/<id>` 与 `/download/<id>`。修改对象编号，验证应用未检查快照所有权。

下载其他用户的 PCAP，分析 FTP 控制流并恢复 Nathan 的登录凭据。

## 2. 建立用户级访问

将恢复的凭据用于 FTP 或 SSH 服务。通过 FTP 可以取得用户目录中的 `user.txt`；也可以通过 SSH 获得交互式用户会话。

提交 User Flag，完成第一阶段。

## 3. 枚举 Linux capabilities

在 Nathan 的会话中检查文件 capability：

```bash
getcap -r / 2>/dev/null
```

重点关注 `/usr/bin/python3.8`。目标为该 Python 可执行文件设置了 `cap_setuid`，允许进程调用 `setuid(0)` 切换到 UID 0。

## 4. 利用 Python cap_setuid

使用 Python 调用 `os.setuid(0)`，验证当前 UID 已变为 0，再读取 Root Flag：

```bash
/usr/bin/python3.8 -c 'import os; os.setuid(0); print(os.getuid()); print(open("/root/root.txt").read())'
```

提交 Root Flag。

## 漏洞链总结

1. 未授权读取其他用户的 PCAP。
2. 从真实 FTP 控制流恢复明文凭据。
3. 凭据复用取得 Nathan 用户访问。
4. 发现 Python 文件的 `cap_setuid` capability。
5. 调用 `os.setuid(0)` 获得 UID 0。
6. 读取并提交 Root Flag。

## 关键实现位置

- `labs/cap/app.py`：真实 tcpdump 快照和 IDOR 路由。
- `labs/cap/Dockerfile`：真实 vsftpd 会话 PCAP、Python 3.8 文件 capability。
- `labs/cap/scripts/entrypoint.sh`：实例 Flag 注入及 FTP、SSH、Web 服务启动。
- `labs/cap/tests/attack_path.py`：独立验证 IDOR、PCAP、FTP 和 live capture。

## 参考资料

- HTB Cap：https://www.hackthebox.com/machines/cap
- 0xdf Writeup：https://0xdf.gitlab.io/2021/10/02/htb-cap.html
- IppSec walkthrough：https://www.youtube.com/watch?v=O_z6o2xuvlw

本题保留公开 Writeup 中的真实技术路径。原始 HTB Web 应用源码未公开，因此本地 Flask 页面是依据观察到的行为重建；FTP、SSH、tcpdump 和 Python capability 均使用真实组件。
