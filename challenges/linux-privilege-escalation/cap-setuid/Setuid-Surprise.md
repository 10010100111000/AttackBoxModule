---
summary: 综合复习网络快照 IDOR 与凭据复用，并利用 Python 文件 capability 完成权限边界突破。
level: hard
lab: cap
---

# 场景

你已经发现网络快照服务存在对象级访问控制问题。现在需要从外部入口开始，对整台主机进行完整安全评估，追踪从 Web 数据泄露到本地权限边界的整个过程。

# 任务

完成从 Web 快照访问到系统最高权限的完整利用链，提交用户 Flag 和 Root Flag。

本题包含两个阶段。第二阶段会重新考察第一阶段的 Web 与凭据发现过程，作为综合复习。

```quiz
title: Root of Trust — User
kind: flag
prompt: |
  从网络快照 IDOR 开始，恢复 FTP 凭据并取得 Nathan 的用户级访问，提交 user Flag。
answer: "TTP{pending}"
match: trim
hint: 完整检查 Web 对象访问控制、PCAP 中的 FTP 控制流以及凭据复用。
```

```quiz
title: Root of Trust — Root
kind: flag
prompt: |
  在取得 Nathan 的访问权限后，检查系统文件 capability，利用实际配置的 Python capability 完成权限提升并提交 root Flag。
answer: "TTP{pending}"
match: trim
hint: 重点检查可执行文件的 Linux capabilities，而不只是传统 SUID 位。
```
