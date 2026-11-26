---
summary: 完整评估博客的认证、导入与会话处理流程。
level: hard
lab: nodeblog
---

# 场景

对博客进行一次完整安全评估。从访问控制开始，追踪文章导入，再分析应用如何处理浏览器会话。

# 任务

通过网站的真实功能完成目标。每个阶段都需要提交对应 Flag；后续挑战会重新考察前面阶段，作为复习和综合验证。

```quiz
title: Flag 01 — Authentication Review
kind: flag
prompt: |
  重新完成认证阶段，提交受保护内容中的第一枚 Flag。
answer: "TTP{y6txbhboebhld66l}"
match: trim
hint: 从应用实际提供的功能和数据流入手，先观察，再验证。
```

```quiz
title: Flag 02 — Import Result Review
kind: flag
prompt: |
  重新完成文章导入阶段，提交第二枚 Flag。
answer: "TTP{fdfh3urqvpj35dcd}"
match: trim
hint: 从应用实际提供的功能和数据流入手，先观察，再验证。
```

```quiz
title: Flag 03 — Application Access
kind: flag
prompt: |
  继续调查应用的会话处理方式，完成最后阶段并提交 Flag。
answer: "TTP{6umc5yaco3okvtmu}"
match: trim
hint: 从应用实际提供的功能和数据流入手，先观察，再验证。
```
