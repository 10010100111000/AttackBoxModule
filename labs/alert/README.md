# Alert — Markdown XSS administrator browser exercise

**Status: full-chain E2E passed.** Two clean instances with different random Flags were solved by the independent HTTP attacker through real target-local Chromium, stored Markdown XSS and loopback-only PHP path traversal. Not an official HTB distribution.

## Web-only learning objective

Reconstruct the observable Web behavior of retired HTB Alert: public Markdown preview, persistent share links, contact submission reviewed by an instance-local administrator browser, loopback-limited message reader, and a real filesystem path traversal in that message reader. Markdown is rendered using the real Python-Markdown parser with raw HTML passthrough, while the bot opens only shared local Markdown pages with genuine Chromium; no stub browser or simulated DOM.

The deployed training boundary is **PHP 8.2 + real Markdown parser + Chromium** in one Alpine container, with a browser process spawned only for queued reviews. The bot reads contact message files; it does not read the private Web Flag directly. A separate public user must investigate the app and discover the trust boundary.

Public original writeup evidence:
- https://0xdf.gitlab.io/2025/03/22/htb-alert.html
- https://www.youtube.com/watch?v=zSBEfW46zd0

Original Linux, Apache Basic Auth, SSH and cron privilege-escalation stages are intentionally excluded. The original PHP/private website assets are unavailable; this is independently written app glue based on public behavior, **not** a byte-for-byte copy.

## Build and local startup

```sh
docker build -t ttp-alert:local -f labs/alert/Dockerfile labs/alert
docker run -d --name ttp-alert --memory 1100m --cpus 2 --pids-limit 256 \
  --security-opt no-new-privileges -e ALERT_USER_FLAG='TTP{example_web_flag}' \
  -p 127.0.0.1:8080:8080 ttp-alert:local
docker inspect -f '{{.State.Health.Status}}' ttp-alert
```

The private goal is a normal file under /opt/alert/private, not an HTTP handler that returns a Flag. An optional instance flag variable replaces the static development placeholder on startup. Removing and recreating the target discards uploaded Markdown and contact messages, and can rotate this flag.

## Verification and release boundary

GitHub Actions builds the genuine PHP/Markdown/Chromium image and an entirely separate HTTP-only player. The player uploads Markdown containing browser JavaScript, shares the resulting link through the contact form, and receives the exact instance Flag **only after genuine target-local Chromium executes the page and reads the private file through the loopback-only messages.php path traversal**. Public direct calls to messages.php remain forbidden. The dedicated E2E runs against two clean instances with different random Flags; it also checks that the default image Flag seed matches the learner Challenge answer.

The current Lab E2E gate is passed. The `.release-blocked` marker remains only for separate platform Worker/Web grading and production integration gates; those are outside this Lab-production task.

## Observed CI results

- [Full-chain two-instance Flag E2E PASS](https://github.com/10010100111000/AttackBoxModule/actions/runs/46046059969). The attacker is a separate container and performs all inputs over HTTP. The target-local browser is part of the target image, not Worker.
- Latest image: **309,342,395 bytes** (~295 MiB); memory after browser proof was **136.6–137.1 MiB** with 57 PIDs (1.1 GiB limit). These are point-in-time readings, not measured peak memory.
- The acceptance runner uses `--cap-drop ALL` and adds only `SETUID`/`SETGID` so the entrypoint can drop to the separate `www-data` and `alertbot` service accounts; `no-new-privileges` remains enabled. No privileged Docker mode or mounted Docker socket.
- Release block remains until an independent two-instance, rotated-Flag-to-goal test and Worker/Web grading integration are verified.
