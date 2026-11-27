# Nibbles — Writeup

## 目标

识别真实 Nibbleblog 4.0.3 CMS，利用 My Image 插件的文件上传缺陷取得 nibbler 用户执行权限，再利用用户可写且被 sudo 允许执行的监控脚本完成 Root 提权。

## 1. 侦察公开站点

先访问首页。页面只显示简单的欢迎内容，不要立即假设它是静态站点。查看 HTML 源码，可以发现指向 `/nibbleblog/` 的注释线索。

访问该目录，检查公开 README、配置文件与用户信息文件。README 显示版本为 Nibbleblog 4.0.3。

## 2. 识别 CMS 管理功能

访问 `/nibbleblog/admin.php`，确认这是原版 Nibbleblog 管理登录页。使用题目提供的默认后台凭据进入控制面板。

在插件管理中找到 My Image 插件，查看其安装与配置页面。该功能需要接收图片文件并将其保存到插件目录。

## 3. 利用插件上传缺陷

检查上游 Nibbleblog 4.0.3 的插件配置控制器。文件上传处理使用 PHP 的 `move_uploaded_file()`，但没有可靠限制上传文件的可执行扩展名。

通过正常的插件配置表单上传 PHP 文件。上传后的文件被放置在 My Image 插件目录中，并由 Apache/PHP 处理。由于 Apache worker 以 nibbler 用户运行，上传文件中的 PHP 代码也以该用户身份执行。

通过执行身份确认当前用户为 nibbler，并读取：

~~~sh
id
cat /home/nibbler/user.txt
~~~

## 4. 检查本地文件与 sudo 权限

在 nibbler 的 home 目录中发现 `personal.zip`。解压后得到监控脚本：

~~~sh
cd /home/nibbler
unzip personal.zip
ls -l personal/stuff/monitor.sh
sudo -l
~~~

监控脚本由 nibbler 所有且可写，而 sudoers 允许 nibbler 以 root 身份执行这个固定路径的脚本。问题在于 sudo 限制了脚本路径，却没有确保脚本内容不可被低权限用户修改。

## 5. 修改监控脚本并提权

将监控脚本内容替换为需要以 root 身份执行的操作，再通过允许的 sudo 命令运行该脚本。验证执行身份为 UID 0 后，读取：

~~~sh
cat /root/root.txt
~~~

提交精确的 Root Flag。

## 漏洞链总结

1. 首页源码暴露 CMS 子目录。
2. 识别原版 Nibbleblog 4.0.3。
3. 登录真实 CMS 管理后台并安装 My Image 插件。
4. 利用插件上传处理缺陷执行 PHP，取得 nibbler 身份。
5. 读取 User Flag。
6. 解压 personal.zip，发现用户可写的监控脚本。
7. 利用 sudo 对固定脚本路径的错误授权取得 root。
8. 读取 Root Flag。

## 真实组件与复现边界

- Nibbleblog 4.0.3：固定上游提交 `6fe138276e82ed604bb35a960327a4ac0b485097`。
- CVE-2015-6967：原版 My Image 插件文件上传缺陷。
- Apache 与 PHP：实际处理上传文件。
- sudo：实际执行被授权的监控脚本。

原题的首页和 `personal.zip` 内容没有公开。本复现对这两部分进行了明确标注的行为重建；CMS 登录、插件上传与 sudo 提权使用真实组件和真实漏洞行为，不使用模拟接口或伪造提权程序。
