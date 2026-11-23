# Bashed — genuine phpbash web shell → sudo scriptmanager → root cron

> Retired HTB Linux machine reconstruction. Uses the original Arrexel/phpbash project under Apache/PHP. Not an official HTB image; isolated Docker network only.

## Player discovery path

1. Scan reveals HTTP/80 only. Browse the ordinary Bashed landing page; it does not link to the developer web shell.
2. Directory enumeration discovers `/dev/phpbash.php`. This is the genuine Arrexel/phpbash 1-file web shell, not a replacement command endpoint. Its original PHP code calls `shell_exec($_POST['cmd'])` and provides a terminal-style browser interface.
3. Commands execute as Apache `www-data`. `sudo -l` reveals `NOPASSWD: ALL` as `scriptmanager`, allowing a shell as that user.
4. Enumerate `/scripts`: `test.py` is owned by scriptmanager and writes to `test.txt`, whose owner is root. A real root cron entry executes every Python file in `/scripts` once per minute. Modify `test.py`, wait for the scheduled execution and obtain Root.
5. User flag is `/home/arrexel/user.txt`; root flag is `/root/root.txt`.

## Upstream and fidelity

- Original web shell: https://github.com/Arrexel/phpbash — the exact upstream `phpbash.php` blob is pinned by Git object hash `dd7ff714ad62ddcf2a06a7a44af9c342b7d83552`; Apache License 2.0 is retained.
- Original writeups: https://0xdf.gitlab.io/2018/12/08/htb-bashed.html ; https://trophyroom.thomaslaurenson.com/hackthebox/bashed/ ; https://adversarial.work/blog/writeup-bashed/
- HTB did not publish its full website source. The public landing page is a small reconstruction; the vulnerable web shell itself is the authentic upstream code. The root cron schedule and file ownership are based on the observed `/scripts/test.py` behavior.
- Runtime is Ubuntu 18.04/PHP 7.2/Apache, whereas the retired host used Ubuntu 16.04. The web shell source and privilege boundary are preserved; package fingerprints may differ.

## Build and acceptance

```bash
docker build -f labs/bashed/Dockerfile -t ttp-bashed:dev labs/bashed
docker run --rm -d --name bashed --network none ttp-bashed:dev
docker inspect -f '{{.State.Health.Status}}' bashed
```

CI uses an independent attacker container. It calls the real phpbash HTTP POST interface as `www-data`, validates the sudo pivot to `scriptmanager`, modifies the actual `/scripts/test.py`, and waits for the real root cron service to execute it. It does not directly execute the modified script as root. The CI then verifies both static flags, per-instance isolation and clean reset.

Static demo flags only: `/home/arrexel/user.txt` and `/root/root.txt`. Production Worker instances must inject `BASHED_STATIC_USER_FLAG`, `BASHED_STATIC_ROOT_FLAG`, and `BASHED_REQUIRE_PRIVATE_FLAGS=1`. Keep production answers outside Git and public GHCR images.
