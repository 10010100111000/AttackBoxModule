# main 分支靶机清单

> 本文是人工阅读入口，不维护第二套状态数据。**靶机状态、CI 工作流、运行证据、提交 SHA 和 backlog 的唯一事实来源是** [`catalog/web-curriculum.json`](../catalog/web-curriculum.json)。
>
> 本清单快照对应 main：`11ae45691e3cfefc42c1502576028246f07aa7b3`（2026-11-28）。状态变化时先更新 catalog，再按需更新本文的说明；不要手工维护重复的完整攻击链描述。

## 当前总览

- **27 台 Lab**
- 当前统一 E2E：14 台通过，13 台待完成（其中 Photobomb 已配置工作流，等待首次运行）
- 旧字段 `lab_ci_status`：24 台 `full_chain_ci`、2 台 `partial`、1 台 `unverified`
- `.release-blocked` 标记：10 台。它与 E2E 状态独立，不能用来判断靶机是否制作完成。

### 已通过当前统一 E2E

以下 14 台已经完成靶机攻击链的独立 CI 验收，不要重复制作或重新排入待办：

| Lab | 目标范围 | E2E 证据 |
|---|---|---|
| Alert | Markdown 存储型 XSS → 管理员 Chromium → loopback 文件读取 → Web Flag | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46047104236) |
| Editorial | SSRF → loopback API → SSH dev/prod → GitPython 3.1.29 → User/Root 双 Flag | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46053249839) |
| Nibbles | Nibbleblog 4.0.3 插件上传 → nibbler → sudo monitor.sh → User/Root | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46061441923) |
| BountyHunter | PHP SimpleXML XXE → php://filter 配置读取 → SSH development → sudo Skytrain Python eval → User/Root | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46066236397) |
| Cap | Dashboard IDOR → real FTP PCAP → credential reuse → SSH → Python cap_setuid → User/Root | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46066988029) |
| Shocker | GNU Bash 4.3 Apache CGI Shellshock → shelly → sudo Perl → User/Root | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46062735563) |
| Bashed | 原版 phpbash → www-data → scriptmanager → root cron → User/Root | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46064377547) |
| Cursed Stale Policy | CSP nonce 重用 → Stored/Blind XSS → 管理员 Chromium → Web Flag | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46051233295) |
| Bike | Handlebars 4.1.1 SSTI → RCE → Web Flag | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/45899503806) |
| Precious | PDFKit 0.8.6 命令注入 → ruby → Web Flag | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/45902207628) |
| GoodGames | SQLite SQLi → 凭据恢复/复用 → Jinja2 SSTI → Web Flag | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46011059390) |
| Devvortex | Joomla 4.2.6 配置泄露 → 管理员模板编辑 → Web Flag | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46017292203) |
| Base | PHP 7.2 登录绕过 → 上传 → SSH → sudo find → User/Root 双 Flag | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46022242878) |
| Intense | SQLite 条件错误 SQLi → SHA-256 长度扩展 → 日志路径遍历 → Web Flag | [CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/46028110921) |

这里的“通过”只表示对应提交的靶机 E2E 已按真实网络攻击路径取回精确 Flag。它不代表 Worker、平台同步或生产部署验收；这些工作不属于本流程。

## 其余 main Lab

下表只显示待处理 Lab 的当前 E2E 状态。不要从 `full_chain_ci` 推断新标准 E2E 已通过；历史完整链记录和当前统一 E2E 是两个不同字段。

| Lab | 当前 E2E | 备注 |
|---|---|---|

| OpenAdmin | pending | PR #65 已合并；真实 xajax → Jimmy → 内网应用 → Joanna/User 路径已由当前 CI 验证，Root 阶段因 Expect 测试脚本私钥路径不一致未完成本次验证。靶机已纳入 main，不宣称本次完整 E2E passed。 |
| Pebbles | pending | 有历史完整链 CI 记录 |
| Photobomb | pending | 已配置单实例独立攻击端 E2E，验证 ImageMagick 命令注入与 sudo PATH 劫持；等待首次 CI 运行 |
| Union | pending | 有历史完整链 CI 记录 |
| Validation | pending | 有历史完整链 CI 记录 |
| Funnel | pending | 部分实现；FTP / SSH / PostgreSQL 服务链，非 Web 主线 |
| Django Debug XSS | pending | 有历史完整链 CI 记录；存在 release-blocked 标记 |
| WonderCMS XSS | pending | 有历史完整链 CI 记录；存在 release-blocked 标记 |
| Usage | pending | 有历史完整链 CI 记录；存在 release-blocked 标记 |
| NodeBlog | pending | 有历史完整链 CI 记录；存在 release-blocked 标记 |
| Zipping | pending | 有历史完整链 CI 记录；存在 release-blocked 标记，另有 ZIP symlink 目标争议 |
| Soccer | pending | 有历史完整链 CI 记录；存在 release-blocked 标记 |
| Trick | pending | 尚未完成统一 E2E；多服务链，暂缓优先处理 |

## 状态定义

- `lab_ci_status`：保留既有目录/历史 CI 分类，不能代替当前 E2E 状态。
- `e2e_ci_status=passed`：该 Lab 的独立攻击端通过真实网络入口完成预期路径，并精确取回当前 Flag。
- `e2e_ci_status=pending`：尚无当前统一标准下的通过记录。
- `release_status=blocked_by_marker`：仓库仍有发布阻塞标记；需结合该 Lab 的具体原因判断，不等于 E2E 失败，也不等于代码未完成。
- `worker_status`：不在本项目靶机制作与 CI 工作范围内。

## 下一步

Cap 与 OpenAdmin 已完成当前阶段的仓库集成。OpenAdmin 的完整 Root E2E 未重新验证，但不阻塞靶机进入平台集成。下一台按 Catalog 中尚未处理的 Lab 顺序选择；Funnel 是非 Web 服务链，Trick 范围较大，暂不优先。

## 文档入口

- [靶机制作与 CI 操作规程](LAB_PRODUCTION_PLAYBOOK.md)：唯一执行流程、工程约束和会话交接。
- [Web 靶机课程设计](WEB_LAB_DESIGN.md)：知识分类、技能梯度、选题原则与教学规划。
- [结构化靶机状态与 backlog](../catalog/web-curriculum.json)：机器状态、证据、候选与队列。
- [技能分类表](../catalog/web-competencies.json)：技能 ID 和验收目标。
- `labs/<slug>/README.md` 与 `writeup.md`：各靶机自己的实现说明与完整解题记录。
