# OpenAdmin — OpenNetAdmin 18.1.1 → credential pivot → SSH key → sudo nano

> Retired HTB Linux machine reconstruction. Uses genuine OpenNetAdmin v18.1.1 source and its original vulnerable xajax handler. This is not an official HTB image. Keep isolated from the public internet.

## Original attack path

1. Nmap finds HTTP/80 and SSH/22. Browse `/ona/` and identify OpenNetAdmin **v18.1.1**.
2. The genuine upstream `www/winc/tooltips.inc.php` defines `ws_ping()` as `shell_exec("ping -n -w 3 -c 3 {$form['ip']}")`. The unauthenticated xajax `window_submit` route allows a crafted `ip` value to append shell commands. This is the original 18.1.1 RCE, not a custom command endpoint. Initial shell runs as Apache `www-data`.
3. Read the actual ONA-generated `www/local/config/database_settings.inc.php`. Its MySQL `ona_sys` password is reused by Linux SSH account `jimmy`.
4. From Jimmy, discover the loopback-only Apache virtual host at `127.0.0.1:52846`. SSH local forwarding exposes the internal PHP application. The source contains a hard-coded SHA-512 password hash; `Revealed` authenticates as Jimmy and the application returns Joanna's encrypted RSA private key.
5. Crack the private-key passphrase (`bloodninjas`) and SSH as `joanna`. `sudo -l` reveals `NOPASSWD: /bin/nano /opt/priv`. Use nano's built-in read/execute command prompt to execute as root.

## Authentic software and explicit reconstructions

- OpenNetAdmin upstream v18.1.1: https://github.com/opennetadmin/ona/tree/v18.1.1
- Original RCE PoC: https://github.com/amriunix/ona-rce
- Original writeups: https://hackindex.io/writeups/openadmin ; https://h4ckron.github.io/htb-writeup-openadmin/ ; https://moisestapia.github.io/htb-writeup-openadmin/
- Original ONA PHP, xajax library, `ws_ping` implementation, schema and CLI installer are retained. The ONA database is initialized using its own `install/installcli.php` installer.
- HTB's internal `index.php`/`main.php` PHP app is not published as an official source tree; the small internal site is an explicit reconstruction of the observed login/hash/private-key behavior. The SHA-512 digest, password reuse, internal port, key passphrase and nano sudo rule follow public writeups.
- Host is Ubuntu 18.04 with PHP 7.2 and MySQL 5.7; package fingerprints may differ from the original host. No vulnerable ONA PHP source or xajax code is replaced.

## Build and test

```bash
docker build -f labs/openadmin/Dockerfile -t ttp-openadmin:dev labs/openadmin
docker run --rm -d --name openadmin --network none ttp-openadmin:dev
docker inspect -f '{{.State.Health.Status}}' openadmin
```

CI starts actual ONA, MySQL, Apache and SSH services on a private Docker network. A separate attacker container checks xajax RCE as `www-data`, the real DB configuration leak, SSH password reuse, SSH local forwarding to port 52846, the internal app's encrypted key, SSH login as Joanna and the real nano command-execution privilege boundary. It also verifies static flags, a second isolated instance and fresh-container reset.

Static demo flags only: `/home/joanna/user.txt` and `/root/root.txt`. Production Worker instances must inject `OPENADMIN_STATIC_USER_FLAG`, `OPENADMIN_STATIC_ROOT_FLAG`, and `OPENADMIN_REQUIRE_PRIVATE_FLAGS=1`. Keep production answers outside Git and public GHCR images.
