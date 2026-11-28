# PG Pebbles — 原题复现研究

> 状态：**Lab 已在 main 实现，历史原版漏洞链 CI 通过；正式 Challenge 已添加。当前统一 E2E 状态仍为 pending。**

- 核心技术：**ZoneMinder 1.29.0 的真实 SQL 注入**，MySQL 数据库文件写入、PHP 执行以及 UDF 权限。
- 起点：扫描得到多个真实端口，浏览后找到 3305 端口 Apache 默认页面；需要枚举目录才能发现 `/zm/`。
- 前端：原版 ZoneMinder 1.29.0 的 HTML/CSS/JS 和控制台，而非用自编前端假装 ZoneMinder。
- 后端：原版 ZoneMinder、Apache/PHP、MySQL 5.7；另有原题的 FTP、SSH、Tomcat 等服务。
- 关键转折：应用 SQLi → 文件写入到 Web 根目录 → PHP `www-data` → MySQL UDF 在原题不安全配置下取得 Root。
- Flag：当前采用静态 Flag。原题 Writeup 主要记录 `/root/proof.txt`；不凭空增加必需的 User 阶段。
- Docker 适配：一个镜像包含多个真实服务，不假定 Compose 多容器；只在隔离练习网络内运行。

**研究、来源、未解决的差异和实际验收清单：** [labs/pebbles/RECONSTRUCTION.md](../../../labs/pebbles/RECONSTRUCTION.md)。

正式 Challenge 正文见 [pebbles.md](pebbles.md)，实现与解题过程见 [Lab README](../../../labs/pebbles/README.md)、[RECONSTRUCTION](../../../labs/pebbles/RECONSTRUCTION.md) 和 [writeup](../../../labs/pebbles/writeup.md)。本目录文件保留为选题与原题来源研究记录。
