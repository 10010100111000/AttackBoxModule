# Soccer — HTB Web-only reconstruction

**Status:** independently verified full Web-chain CI PASS on two fresh isolated targets. Worker and Web scoring integration remain unverified. This is not the unavailable original private HTB source.

## Exploit sequence

1. Discover a public City League sports homepage, then enumerate the /tiny/ manager.
2. Reach actual upstream **Tiny File Manager 2.4.3**, release commit `1dbe7c5339ad955fcb08d01d256f591a3c83d713`. Its vendor-default admin credentials and *real* `move_uploaded_file` upload handling create a PHP foothold within the web-writable directory.
3. Read Nginx virtual-host configuration as the PHP web user, revealing `soc-player.soccer.htb`. PHP cannot directly read the target flag or Node source.
4. Explore the ticket office and its real JSON WebSocket protocol on TCP 9091.
5. A Node `ws` service interpolates a user-supplied ticket id into a genuine MariaDB query. Boolean ticket-exists responses permit SQLi against actual database records.
6. Blind-extract the per-instance Web goal stored as `accounts.goal`. There is **no** simulated SQL interpreter or hardcoded answer endpoint.

**Original-vs-reconstructed:** Original Tiny File Manager 2.4.3 is fetched from a pinned upstream commit unchanged, with separate lab configuration to limit its writable root. The public site, ticket office, MariaDB data and Node endpoint are independent reconstructions based on published HTB Soccer writeups, not original inaccessible HTB source. The WebSocket/MySQL mechanism is genuine. SSH and `doas/dstat` system privilege escalation from the full HTB machine are intentionally omitted: this is a **Web-only** lab with one Web goal Flag.

## Isolated local build

```bash
docker build -t ttp-soccer:local -f labs/soccer/Dockerfile labs/soccer
docker run -d --name soccer-lab --security-opt no-new-privileges \
  --memory 1g --cpus 1.5 --pids-limit 220 \
  -e SOCCER_USER_FLAG='TTP{example_web_flag}' \
  -p 127.0.0.1:8080:8080 -p 127.0.0.1:9091:9091 ttp-soccer:local
docker inspect -f '{{.State.Health.Status}}' soccer-lab
```

When using a browser, resolve both `soccer.htb` and `soc-player.soccer.htb` to the private target address. Keep port 9091 VPN-only; the browser connects directly to its WebSocket.

The target owns its Flag: `SOCCER_USER_FLAG` is copied to a root-readable seed at startup and inserted in the MariaDB goal record. The Worker schedules the target but neither returns nor validates a Flag. The Web backend handles scoring.

## Acceptance and release gates

`.github/workflows/soccer.yml` builds the real container and a separate attacker container. The attacker uses HTTP plus WebSocket only: original manager login, native PHP upload, nginx discovery, normal ticket check, real MariaDB truth/false SQL behavior, actual account enumeration, and entire Web goal extraction on **two fresh instances with different flags**. It checks health, Docker capabilities, mounts, image size and memory. Verified by [GitHub Actions run 45478649027](https://github.com/10010100111000/AttackBoxModule/actions/runs/45478649027): both fresh targets solved in full via network-only HTTP and WebSocket attacker. Flags rotated between instances. Actual image: **165,242,892 bytes**; observed memory **118 MiB / 117.3 MiB**. Worker sandbox and Web backend scoring still need separate release checks. Platform Worker and Web backend integration are separate release checks.

Sources: https://www.hackthebox.com/machines/Soccer ; https://0xdf.gitlab.io/2023/06/10/htb-soccer.html ; https://github.com/prasathmani/tinyfilemanager/releases/tag/2.4.3
