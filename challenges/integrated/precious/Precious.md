---
summary: 从 URL 转 PDF 的正常功能入手，调查生成文件暴露的组件信息。
level: beginner
lab: precious
---

# 场景

一项在线服务可以将指定网页转换为 PDF。服务没有公开说明使用了什么转换组件，但生成的文件可能保留有关生成器的信息。

请从正常的网页转换功能开始，观察输入 URL 的处理方式，并调查生成文件中的技术线索。

# 任务

识别 PDF 生成组件及其存在的安全问题，利用 Web 服务处理 URL 时的缺陷，读取 Web 服务账户权限范围内的目标文件并提交 Flag。

本题为 Web 专项，只要求取得 Web Flag，不要求 SSH 凭据复用、Linux Root 提权或 YAML 反序列化。

```quiz
title: Precious
kind: flag
prompt: |
  从正常的 URL 转 PDF 功能开始调查，识别生成器及其版本，利用其真实漏洞读取 Web 进程可访问的目标文件。
answer: "TTP{aaaaaaaaaaaaaaaa}"
match: trim
hint: 先检查生成的 PDF 文件元数据，再根据其中暴露的组件名称和版本查找公开安全公告。
```
