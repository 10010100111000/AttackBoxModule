# Alert — Markdown XSS administrator browser exercise

**Status: real browser and privileged-localhost traversal CI PASS. Final Web Flag extraction CI remains pending.** Not an official HTB distribution.

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

GitHub Actions now builds the genuine PHP/Markdown/Chromium image and an entirely separate HTTP-only player. The player uploads a Markdown document containing browser JavaScript, shares the resulting link through the contact form, and receives a non-sensitive callback **only after genuine target-local Chromium executes the page and retrieves PHP source through the loopback-only messages.php directory traversal**. Public direct calls to messages.php remain forbidden. This demonstrates real stored XSS, cross-user review and native filesystem traversal, but does not establish end-to-end Flag extraction or platform grading.

Remain blocked from release until independently reproduced attack-chain CI proves actual JavaScript execution in Chromium, local-only message path traversal, extraction of the correctly rotated Web goal from two clean instances, and resource usage during review. Worker integration and platform flag submission are separate additional gates.

## Observed CI results

- [Real Chromium and source-read proof CI PASS](https://github.com/10010100111000/AttackBoxModule/actions/runs/45474730425). The attacker is a separate container and performs all inputs over HTTP. The browser is in the target image, not Worker.
- Image: **309,343,624 bytes** (~295 MiB); idle memory **27.47 MiB**, memory recorded after browser proof **135 MiB**. These are point-in-time readings, not peak memory during browser startup.
- No privileged Docker mode or added Linux capabilities, and no mounted Docker socket.
- Release block remains until an independent two-instance, rotated-Flag-to-goal test and Worker/Web grading integration are verified.
