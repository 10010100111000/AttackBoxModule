---
summary: 已取得 xander 账户。审计其免密归档维护命令，以及归档工具对文件列表参数的解释方式。
level: intermediate
lab: usage
---

# 场景

你已经取得服务器上的 xander 账户。系统为该账户配置了一项免密归档维护任务，用于生成项目备份。

请检查该任务调用的程序、参数和文件列表处理方式，判断普通文件名是否可能被解释为额外的程序输入。

# 任务

利用真实归档工具与 sudo 授权之间的权限边界问题，读取 root-only 文件并提交 Root Flag。

```quiz
title: Archive Maintenance
kind: flag
prompt: |
  审计 xander 的 sudo 归档命令，利用真实 p7zip 16.02 的文件列表处理行为读取 /root/root.txt 并提交 Root Flag。
answer: "TTP{xwzjtwluo47hecaf}"
match: trim
hint: 重点研究 7za 对以特殊前缀开头的文件列表参数的处理方式。
```
