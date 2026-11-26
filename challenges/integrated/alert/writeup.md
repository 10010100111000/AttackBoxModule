# Blind Review — Writeup

## 目标

通过 Alert 的 Markdown 上传与分享流程，利用管理员审阅浏览器中的跨用户信任边界，读取仅允许服务器本机访问的消息读取器所能访问的 Web Flag。

本题是 Web-only 练习，不包含 Linux Root 提权。

## 1. 观察 Markdown 上传与分享

访问首页，使用 Markdown 上传功能提交一份普通文档。上传成功后，应用会生成类似下面的分享地址：

```text
/visualizer.php?link_share=<random>.md
```

打开分享地址，确认文档由服务端 Markdown 渲染器转换为 HTML。检查渲染结果时，注意原始 HTML 是否被保留，以及分享页面是否会在管理员浏览器中打开。

## 2. 观察 Contact 审阅流程

Contact 页面允许提交邮件地址和消息。服务端会把消息写入本地队列，管理员 Bot 随后检查其中是否包含受支持的 Markdown 分享链接，并使用真实 Chromium 打开该链接。

关键点是：上传文档由玩家控制，但打开分享链接的浏览器属于靶机内的管理员审阅环境。需要从实际浏览器上下文分析同源访问和本地资源可达性。

## 3. 构造 Stored XSS

在 Markdown 文档中嵌入原始 HTML/JavaScript。由于应用使用真实 Python-Markdown 渲染，并允许 HTML passthrough，浏览器会执行文档中的脚本。

示例逻辑：

```html
<script>
fetch("/messages.php?file=../../../opt/alert/private/web-flag.txt")
  .then(response => response.text())
  .then(body => {
    // 从实际响应中提取 Flag，再发送到你控制的接收端。
  });
</script>
```

将该文档上传并打开生成的分享链接，确认脚本在分享页面的浏览器上下文中执行。

## 4. 利用管理员浏览器访问 Loopback-only Reader

普通玩家直接访问 `/messages.php` 会收到 HTTP 403，因为该页面只接受来自 `127.0.0.1` 或 `::1` 的请求。

管理员 Chromium 运行在靶机容器内部，访问同一站点时连接的是本机地址，因此请求满足该页面的 Loopback 检查。

`messages.php` 使用用户提供的 `file` 参数拼接消息目录路径，并调用 `file_get_contents`，没有阻止目录穿越。利用相对路径可以让它读取 Web Flag 文件：

```text
/messages.php?file=../../../opt/alert/private/web-flag.txt
```

这不是专门返回 Flag 的伪造 API，而是对真实 PHP 文件读取功能和路径处理缺陷的利用。

## 5. 让管理员打开分享链接并接收结果

将生成的分享链接提交到 Contact 表单。Bot 从消息队列读取链接并启动 Chromium。文档中的脚本在管理员浏览器上下文执行，读取上述本地资源，再把响应中的 Flag 发送到玩家控制的 HTTP 接收端。

最终提交接收到的 Flag。

## 漏洞链总结

1. Markdown 原始 HTML 被保留并在分享页面渲染。
2. 管理员 Bot 会打开用户提交的分享链接。
3. 管理员浏览器与靶机 Web 服务处于同一容器，能够访问 Loopback-only 页面。
4. `messages.php` 的文件读取参数存在路径穿越。
5. Stored XSS 将本地读取结果带回玩家。

## 关键源码位置

- `labs/alert/site/visualizer.php`：上传、分享与 Markdown 渲染。
- `labs/alert/site/contact.php`：联系消息写入与管理员审阅队列。
- `labs/alert/bot/review.py`：管理员 Chromium 审阅流程。
- `labs/alert/scripts/render_md.py`：真实 Python-Markdown 渲染器。
- `labs/alert/site/messages.php`：Loopback 检查与存在漏洞的文件读取。

## 复现边界

本靶机复刻的是公开 Writeup 中可观察到的 Web 行为和关键漏洞组合，不是原始 HTB Alert 镜像的逐字节复制。原题中的 Linux、SSH、cron 和 Root 提权阶段不属于本 Challenge。
