# Editorial — Writeup

## 目标

从出版社的封面预览功能发现服务器端请求伪造（SSRF），访问仅监听 loopback 的 Flask API，取得开发账户，再通过 Git 历史恢复生产凭据，最后利用生产部署助手所调用的真实 GitPython 3.1.29 完成提权。

## 1. 侦察公开网站

先浏览首页、About 和 Publish with us 页面。投稿页面包含封面 URL 预览功能。提交普通外部图片地址，观察响应：服务器会把获取到的内容保存到静态上传目录，并返回一个不可预测的文件路径。

这里的关键不是浏览器直接加载图片，而是目标服务器主动请求用户提供的 URL。

## 2. 发现内部 API

将封面 URL 指向目标自身的 loopback 地址和内部 API 端口。虽然外部攻击端无法直接连接该端口，但服务器端预览请求可以访问本机服务。

从 API 根路径开始枚举返回的 links，再检查 metadata 与 authors 消息。响应中包含编辑团队的 onboarding 信息，其中包括开发账户的临时登录凭据。

## 3. 取得 dev 账户

使用发现的凭据连接目标 SSH 服务。登录后确认当前身份，并读取普通用户 Flag：

~~~sh
id
cat /home/dev/user.txt
~~~

随后检查开发目录中的 Git 仓库：

~~~sh
git -C /home/dev/apps log --oneline
git -C /home/dev/apps show HEAD~1:api_notes.py
~~~

当前版本已经移除了生产账户凭据，但早期提交仍保留了旧配置。Git 历史因此成为凭据泄露来源。

## 4. 取得 prod 账户

使用历史提交中发现的生产凭据登录 SSH。先确认账户权限，不要直接假设该账户拥有 root 权限：

~~~sh
id
sudo -n -l
~~~

可以看到 prod 只被允许通过指定的 Python 部署助手执行操作，而不是任意运行 root 命令。

## 5. 分析部署助手与 GitPython

检查 sudoers 指定的脚本及其依赖。部署助手调用真实的 GitPython 3.1.29 `Repo.clone_from`，并将调用者提供的仓库地址交给 Git。

GitPython 3.1.29 受到 CVE-2022-24439 影响。结合脚本启用的 Git remote transport 行为，仓库地址不再只是普通的数据参数，而可能改变 Git 子进程的执行行为。

在受限 sudo 上下文中触发该真实组件的漏洞后，Git 子进程以 root 身份执行。不要把它替换成模拟的提权接口；本题使用实际 GitPython 包和系统 Git。

## 6. 验证 Root 并读取 Flag

先通过文件所有者或进程身份确认执行上下文确实为 UID 0，再通过同一条真实漏洞路径访问 root 专属文件，读取：

~~~sh
cat /root/root.txt
~~~

将精确的 Root Flag 提交到题目。

## 攻击链总结

1. 公开封面预览功能发起真实服务器端 HTTP 请求。
2. SSRF 访问仅监听 loopback 的 Flask metadata API。
3. API 泄露 dev 账户 onboarding 凭据。
4. SSH 登录 dev，读取 User Flag。
5. 检查 Git 历史，恢复已从当前版本删除的 prod 凭据。
6. SSH 登录 prod，发现受限 sudo 部署助手。
7. 利用真实 GitPython 3.1.29 与 Git remote transport 行为取得 UID 0。
8. 读取 Root Flag。

## 关键组件

- Flask 2.3.3：公开网站与内部 metadata API。
- Nginx：公开 HTTP 入口。
- OpenSSH：dev / prod 账户入口。
- Git：保留真实的两次提交历史。
- GitPython 3.1.29：存在漏洞的部署依赖。
- sudoers：将生产账户限制到指定部署助手。

## 复现边界

这是基于公开行为与公开资料独立重建的训练环境，不是 HTB 官方镜像，也不声称拥有原始私有源码。SSRF、内部 API、SSH、Git 历史和 GitPython 执行链均由真实组件构成。
