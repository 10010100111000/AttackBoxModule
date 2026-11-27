# Bashed — Writeup

## 目标

发现公开首页没有链接的原版 Arrexel/phpbash 工具，利用其真实 PHP Shell 取得 www-data 执行权限，再通过 sudo 切换到 scriptmanager，修改 root cron 定期执行的 Python 脚本，最终读取 Root Flag。

## 1. 侦察公开网站

先访问首页，观察网站只提供普通介绍与开发环境提示。查看 HTML 源码和站点目录，不要假设首页列出了所有资源。

通过目录枚举发现开发目录下的 phpbash.php。该文件是原版 Arrexel/phpbash 单文件 Web Shell，而不是本项目另写的命令执行接口。

## 2. 调查 phpbash

访问开发工具，观察浏览器终端的请求方式。提交普通命令并检查执行身份：

~~~sh
whoami
id
~~~

命令由 PHP 的 shell_exec() 调用系统 Shell 执行，进程身份为 Apache 的 www-data。

## 3. 取得 scriptmanager 身份

检查当前账户的 sudo 权限：

~~~sh
sudo -l
~~~

www-data 被允许免密切换到 scriptmanager。使用该授权检查 scriptmanager 的身份与脚本目录权限：

~~~sh
sudo -u scriptmanager id
ls -la /scripts
~~~

## 4. 分析 root cron

检查系统 cron 配置，发现 root 每分钟执行 /scripts 目录中的 Python 脚本。目录和 test.py 由 scriptmanager 管理，因此该账户能够修改一个会被 root 定期执行的文件。

确认 cron 任务的实际命令、运行身份和文件权限，不要把“脚本可以写入”误认为“脚本已经以 root 执行”。

## 5. 通过真实 cron 取得 Root

修改 /scripts/test.py，使其在下一次 root cron 调度时执行。等待真实定时任务运行后，验证执行身份确实为 UID 0，并读取 /root/root.txt。

CI 使用相同的网络攻击路径：攻击端只通过 phpbash HTTP 界面修改脚本，并等待 root cron；不会直接以 root 身份调用修改后的脚本。

## 攻击链总结

1. 公开网站侦察与目录枚举。
2. 发现原版 Arrexel/phpbash Web Shell。
3. PHP shell_exec 以 www-data 身份执行命令。
4. sudo 免密切换到 scriptmanager。
5. 修改 root cron 定期执行的 /scripts/test.py。
6. 等待真实 root cron 调度并读取 Root Flag。

## 复现边界

- Web Shell 使用 Arrexel/phpbash 原版代码，固定上游 Git blob hash dd7ff714ad62ddcf2a06a7a44af9c342b7d83552。
- Apache/PHP 使用真实 shell_exec()。
- sudoers 和 cron 均由系统原生服务执行。
- HTB 未公开完整原始首页源码；首页为明确标注的独立重建。
- 不使用容器逃逸、伪造提权接口或测试专用 root 执行入口。
