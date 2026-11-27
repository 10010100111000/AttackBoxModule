# Linux 权限提升

本专题按真实权限边界组织专项目标。重点包括 sudo、SUID、Capabilities、ACL、Cron、systemd 等配置与攻击链。

## 题目准入

每道题须有明确的首次可见入口、主要技术关口、后续转折、可复现性和独立学习价值；不因为凑数量而重复同一利用方式。

## 当前可运行挑战

- [Nibbles — System Monitor](nibbles/sudo-monitor.md)：复用 labs/nibbles，考察用户可写 sudo 脚本。
- [Shocker — Perl Maintenance](shocker/sudo-perl.md)：复用 labs/shocker，考察 sudo 授权 Perl 的权限边界。
- [Bashed — Scheduled Maintenance](bashed/root-cron.md)：复用 labs/bashed，考察 scriptmanager 可写脚本与 root cron 执行边界。
- [BountyHunter — Skytrain Validator](bountyhunter/skytrain-eval.md)：复用 labs/bountyhunter，考察 sudo 授权程序中的 Python eval。

多个 Challenge 可以映射到同一个 Lab；不要为同一运行环境复制 Docker 镜像。README.md 用于专题索引，不会作为挑战导入。
