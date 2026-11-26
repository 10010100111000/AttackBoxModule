# Alert — Markdown XSS administrator browser exercise

**Status: real two-instance Web Flag extraction acceptance PASS.** Worker integration and AttackBox grading remain separate release gates. Not an official HTB distribution.

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

GitHub Actions now builds the genuine PHP/Markdown/Chromium image and an entirely separate HTTP-only player. The player uploads a Markdown document containing browser JavaScript, shares the resulting link through the contact form, and receives a non-sensitive callback **only after genuine target-local Chromium executes the page and retrieves PHP source through the loopback-only messages.php directory traversal**. Public direct calls to messages.php remain forbidden. This proves end-to-end Flag extraction: the actual per-instance Web Flag was returned to the external HTTP player by genuine target-local Chromium after the stored Markdown XSS and loopback-only PHP path traversal.

The two-instance browser/Flag acceptance is complete. Keep the release block until Worker lifecycle and AttackBox Flag submission/grading are verified. Do not expose the vulnerable service directly to the public Internet.

## Observed CI results

- [Real two-instance Web Flag extraction CI PASS](https://github.com/10010100111000/AttackBoxModule/actions/runs/45874359031). Two clean targets used distinct random Flags; each real Chromium admin review returned its exact instance Flag to the separate HTTP player.
- [Earlier Chromium/source-read proof](https://github.com/10010100111000/AttackBoxModule/actions/runs/45474730425).
- Image: **309,343,624 bytes** (~295 MiB); idle memory **27.47 MiB**, memory recorded after browser proof **135 MiB**. These are point-in-time readings, not peak memory during browser startup.
- The acceptance runner uses `--cap-drop ALL` and adds only `SETUID`/`SETGID` so the entrypoint can drop to the separate `www-data` and `alertbot` service accounts; `no-new-privileges` remains enabled. No privileged Docker mode or mounted Docker socket.
- Image: **309,342,697 bytes** (~295 MiB); memory after browser proof: **137.4 MiB** in each run (57 PIDs), with a 1.074 GiB container limit. These are point-in-time readings, not peak-memory guarantees.
- Two-instance acceptance completed on GitHub-hosted ephemeral Linux Runner; no production server or Worker was used.
