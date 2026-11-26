# Bike — Writeup

## 目标与范围

本题复现 Bike 的 Web 入口，核心问题是服务端将用户提交的 `email` 值拼接进 Handlebars 模板源码，再交给 Handlebars 编译执行。

这是 Web-only 题目，目标是通过 HTTP 请求完成模板注入并取得一个 Flag。SSH 端口只作为服务枚举信息，不构成额外登录或提权阶段。

## 1. 侦察

先枚举开放端口与服务：

```bash
nmap -sC -sV -p22,80 <TARGET>
```

访问 Web 服务：

```bash
curl -i http://<TARGET>/
```

页面提供一个邮箱订阅表单。提交普通值，观察请求与响应：

```bash
curl -i -X POST http://<TARGET>/ \
  --data-urlencode 'email=analyst@example.test'
```

邮箱值会出现在响应页面中。此时只能确认输入会被处理并回显，尚不能据此断定存在模板注入。

## 2. 发现模板解析行为

向邮箱字段提交一个不符合 Handlebars 语法的模板表达式：

```bash
curl -i -X POST http://<TARGET>/ \
  --data-urlencode 'email={{7*7}}'
```

应用返回模板解析错误。结合输入位置和响应堆栈，可以继续调查服务端模板处理过程。

源码中使用的组件版本为 Handlebars 4.1.2。问题不只是将输入作为普通模板变量传入，而是先把输入拼接到模板源码，再调用 `handlebars.compile()`。因此用户控制的内容会进入模板解析阶段。

## 3. 利用 SSTI 执行命令

本题使用 Handlebars 的构造函数访问链，最终调用 Node.js 的 `child_process`。仓库提供独立 HTTP 利用脚本，攻击端只通过目标 Web 端口发送请求：

```bash
python3 exploit.py --url http://<TARGET>
```

脚本先执行 `id -un`，确认命令执行上下文，再读取目标 Flag。它不依赖 CI 的预期答案变量，也不会访问目标容器的 Docker 管理接口。

## 4. 提交 Flag

`exploit.py` 会在同一条命令执行链中读取 `/root/flag.txt`，Flag 会显示在 HTTP 响应内容中。将取得的值提交到平台即可完成本题。

## 5. 关键原因

漏洞根因是把不可信输入拼接进模板源码：

- 不安全：用户输入先进入模板字符串，再调用模板编译器。
- 安全做法：模板源码保持固定，将用户输入作为模板上下文数据传入；同时避免把不可信内容解释为模板语法。

## 验收边界

`.github/workflows/bike.yml` 使用独立攻击端容器，通过隔离 Docker 网络访问真实 Web 服务，依次检查普通输入、模板解析错误、命令执行身份和精确 Flag 返回值。攻击端不挂载靶机文件系统、不使用 Docker socket，也不通过 `docker exec` 读取答案。

本题只有一个 Web Flag；不包含 SSH 登录、Linux 提权或第二个 Root Flag 阶段。
