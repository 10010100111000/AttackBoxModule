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

## Writeup

The learner-facing Challenges and their focused objectives are listed below. The discovery-led solution and the exact test-harness limitation are documented in [writeup.md](writeup.md).

## Challenge reuse

The following learner Challenges share this one Lab image and the same OpenNetAdmin / internal PHP / SSH environment:

- [OpenAdmin](../../challenges/startpoint/openadmin/OpenAdmin.md): integrated xajax → credential pivot → Joanna → nano root path.
- [Network Diagnostics](../../challenges/command-injection/openadmin/ona-xajax-rce.md): focused OpenNetAdmin xajax command-injection and credential-discovery objective.
- [Restricted Editor](../../challenges/linux-privilege-escalation/openadmin/nano-sudo.md): focused sudo nano privilege-boundary objective.

The focused Challenges reuse the corresponding User or Root Flag from the integrated Challenge; they do not create separate Docker images or duplicate the vulnerable environment.

## Build and test

```bash
docker build -f labs/openadmin/Dockerfile -t ttp-openadmin:dev labs/openadmin
docker run --rm -d --name openadmin --network none ttp-openadmin:dev
docker inspect -f '{{.State.Health.Status}}' openadmin
```

The dedicated `.github/workflows/openadmin-e2e.yml` starts actual ONA, MySQL, Apache and SSH services on one private Docker network. One independent non-root attacker verifies xajax RCE as `www-data`, the real DB configuration leak, SSH password reuse, SSH local forwarding to port 52846, the internal app's encrypted key, SSH login as Joanna and the real nano command-execution privilege boundary. It checks the exact random User and Root Flags generated for that single CI instance. It does not start a second target instance or use `docker exec` as the attacker. The historical E2E verified the chain through Joanna and the exact User Flag. Its Root-stage Expect script hardcodes /tmp/joanna_id_rsa while the attacker passes the actual key in a temporary directory argument; the script ignores that argument. We are not rerunning E2E solely for this harness path issue. This does not establish a target-side nano failure, but the current unified E2E status remains pending.

Static demo flags only: `/home/joanna/user.txt` and `/root/root.txt`. Production Worker instances must inject `OPENADMIN_STATIC_USER_FLAG`, `OPENADMIN_STATIC_ROOT_FLAG`, and `OPENADMIN_REQUIRE_PRIVATE_FLAGS=1`. Keep production answers outside Git and public GHCR images.
