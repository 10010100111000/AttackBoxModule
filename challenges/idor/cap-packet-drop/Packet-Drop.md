---
summary: 从安全仪表板的历史网络快照入手，调查未授权对象访问与凭据泄露。
level: medium
lab: cap
---

# 场景

一套网络安全仪表板为用户提供网络状态和流量快照功能。你发现快照通过数字编号访问，但应用似乎没有明确说明这些记录是否属于当前用户。

请从公开仪表板开始，检查快照的访问方式和下载行为，判断是否能够取得其他用户的网络数据。

# 任务

通过 Web 应用中的对象级访问控制缺陷取得历史网络快照，分析其中暴露的信息，并使用发现的凭据访问对应服务，提交用户 Flag。

本题重点考察 IDOR / Broken Object Level Authorization、PCAP 分析和凭据复用。

```quiz
title: Packet Drop
kind: flag
prompt: |
  调查网络快照的编号与下载访问控制，取得其他用户的真实流量记录，从中发现可用凭据并完成用户级访问，提交 user Flag。
answer: "TTP{ocg7a5dd5zdd7hnq}"
match: trim
hint: 先观察正常快照的 URL 和编号，再比较未经授权的其他编号是否也能访问。下载后检查 PCAP 中的应用层协议数据。
```
