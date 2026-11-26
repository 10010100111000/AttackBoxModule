# HTB Headless — Blind XSS / Command Injection / sudo path hijack

**Status: implementation and non-exploit integration checks are being completed.** This is a reconstruction of the retired HTB machine's observable application and OS configuration, not the original VM image.

## Intended challenge path

1. Enumerate the Werkzeug web application on TCP 5000 and discover /support and /dashboard.
2. Inspect the support form and the signed is_admin cookie.
3. Understand how the support handler stores request headers in an HTML report.
4. Discover that the User-Agent is rendered without escaping in hackattempt.html. The real Chromium reviewer opens stored reports in the administrator browser context.
5. Use the resulting admin session to access /dashboard.
6. Inspect the report-generation request and trace the date value into the report helper. The handler runs as the real dvir service account.
7. Read /home/dvir/user.txt.
8. Enumerate sudo -l, inspect /usr/bin/syscheck, and notice its relative ./initdb.sh call.
9. Investigate the writable working directory and the root-authorized script to reach /root/root.txt.

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
      ttp-headless:local

    docker exec headless-lab /usr/local/bin/headless-smoke-test

    docker inspect -f '{{.State.Health.Status}}' headless-lab

Flags are static challenge data copied into the image from flags/user.txt and flags/root.txt. The Worker does not generate, rotate, inject, store or grade Flags. It only manages the target container and sandbox lifecycle. The Web backend/challenge system owns challenge definitions and submitted-Flag validation.

The container needs no privileged mode, host network, Docker socket or host filesystem mount. Do not expose it directly to the public Internet. The production Worker should place the target and its AttackBox on the intended private network. The Worker must not apply no-new-privileges to this target: the original sudo stage requires a normal setuid transition inside the container. This does not require privileged mode or host capabilities.

## Flag files

- flags/user.txt is copied to /home/dvir/user.txt, owner dvir, mode 0400.
- flags/root.txt is copied to /root/root.txt, owner root, mode 0600.
- Recreating the container recreates the same static challenge Flags. There is no Flag Rotation or per-instance Flag generation.

## CI policy

CI is intentionally non-offensive. It checks:

- image build, container startup and Docker health;
- homepage and support page responses;
- ordinary user authorization denial;
- normal support-form submission and report-file persistence;
- real Chromium fetching and rendering the stored report page using a harmless marker;
- normal dashboard report generation with a normal date;
- Flask service identity, writable application directory and exact Flag file ownership/modes;
- sudoers syntax, the allowed syscheck entry, its expected relative-path dependency and SSH listener.

CI does **not** send XSS payloads, steal cookies, inject shell commands, open reverse shells, exploit sudo, read a Flag through the challenge path, or attempt container/host escape.

These integration checks prove that the challenge's real services and prerequisites are connected and functioning. They do not claim to prove exploitability by themselves. Vulnerability behavior must remain source-backed and be reviewed against the disclosed original implementation; any manual acceptance record must be explicit rather than silently treating a smoke test as a completed exploit-chain test.

## Resource measurements

Re-measure image size, idle memory and peak memory while Chromium reviews a report on the CI runner. Do not treat a previous idle-only measurement as peak resource usage.
