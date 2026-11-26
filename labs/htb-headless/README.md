# HTB Headless — Blind XSS / Command Injection / sudo path hijack

**Status: implementation in progress.** The Docker image and service wiring are authored but not built or smoke-checked. Do not release.

## Attack path

1. Enumerate the Werkzeug web application on TCP 5000 and discover /support and /dashboard.
2. Inspect the support form and the signed is_admin cookie.
3. Trigger the support handler's real WAF/report path using the message field. The handler stores the HTTP headers in an HTML report.
4. Discover that the User-Agent is rendered without escaping in hackattempt.html. The in-container Chromium reviewer visits stored reports as an admin browser; the browser is the blind-XSS victim.
5. Use the resulting admin session cookie to access /dashboard.
6. Inspect the report-generation request and trace the date value into os.popen(f"bash report.sh {date}").read(). This executes as the real dvir service account.
7. Read /home/dvir/user.txt.
8. Enumerate sudo -l, inspect /usr/bin/syscheck, and notice its relative ./initdb.sh call.
9. Create the expected helper in the writable working directory and invoke the real sudo-authorized script to reach /root/root.txt.

## Runtime

- Debian 12 slim / Python 3.11.2
- Python 3.11.2, Werkzeug 2.2.2 (observed); Flask 2.2.2 is the reconstruction pin, itsdangerous 2.1.2
- Chromium headless CLI for the admin report-review process
- OpenSSH server on TCP 22
- Flask/Werkzeug on TCP 5000
- dvir is UID/GID 1000 and owns the writable application working directory
- /usr/bin/syscheck is root-owned and matches the disclosed script
- dvir may run only /usr/bin/syscheck through the lab sudoers entry

The app's public source excerpt and exact vulnerable data flows are documented in docs/research/HTB_HEADLESS_SOURCE_AUDIT.md.

## Local run

    docker build -t ttp-headless:local -f labs/htb-headless/Dockerfile labs/htb-headless

    docker run -d --name headless-lab \
      --memory 768m --cpus 2 --pids-limit 192 \
      --security-opt no-new-privileges=false \
      -p 127.0.0.1:5000:5000 -p 127.0.0.1:2222:22 \
      -e HEADLESS_USER_FLAG='TTP{local_user_flag}' \
      -e HEADLESS_ROOT_FLAG='TTP{local_root_flag}' \
      ttp-headless:local

    docker inspect -f '{{.State.Health.Status}}' headless-lab

The container needs no privileged mode, host network, Docker socket or host filesystem mount. Do not expose it directly to the public Internet. The production Worker should place the target and its AttackBox on the intended private network. The Worker must not apply no-new-privileges to this target: the original sudo stage requires a normal setuid transition inside the container. This does not require privileged mode or host capabilities.

## Flags and reset

The Worker supplies both opaque per-instance values. The target writes the User Flag to /home/dvir/user.txt (dvir-readable) and the Root Flag to /root/root.txt (root-only). No production Flag is embedded in the image. Destroy/recreate starts with empty report storage and a fresh pair of Flags.

## CI policy

CI checks only:
- image build;
- container startup and health;
- homepage and support form response;
- SSH listener;
- Chromium admin-review process availability.

It must not automate XSS payloads, cookie exfiltration, command injection, reverse shells, sudo exploitation or Flag extraction. Full attack-path verification is a manual review against a fresh instance.

## Known blockers

- Docker build not yet confirmed.
- Chromium dependencies and image size not measured.
- Admin reviewer has not yet been observed processing a report in a running container.
- Flask app UID, writable report directory and syscheck working directory need smoke verification.
- Worker network access to the AttackBox and dynamic Flag injection remain unverified.
