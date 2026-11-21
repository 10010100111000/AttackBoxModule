# Credential Gate — SQL injection authentication bypass

> **First implementation:** An original training app inspired by the exploitation patterns in OffSec PG Cockpit and HTB Magic. This is not an official or copied machine. It contains a *real, intentionally vulnerable SQL authentication query* and must be run only on an isolated training network.

## Learning objective

- **Starting point:** The public Northstar Dispatch website exposes an operator login.
- **Core vulnerability:** SQL injection through the username field of POST /login. SQL comments can remove the password condition from an unsafe string-interpolated SQL query.
- **Turning point:** The injected session has the role of the selected database user. An administrator can access a restricted quarterly control CSV export.
- **Win condition:** Retrieve the static flag from the restricted report. This is a **Web-only** beginner challenge, not a fake user-to-root machine.

This differs from the existing GoodGames lab: no SSTI, password reuse, secondary host, or container escape.

## Research

- [OffSec PG Cockpit: third-party writeup](https://hackindex.io/writeups/cockpit): SQLi login leads to a management console and later Linux escalation.
- [0xdf: HTB Magic](https://0xdf.gitlab.io/2020/08/22/htb-magic.html): login bypass, upload processing, and SUID escalation.
- [0xdf: HTB Union](https://0xdf.gitlab.io/2021/11/22/htb-union.html): manual UNION SQLi, reserved for the next exercise.

We reference their teaching structures, not their logos, source code, flags, or artwork.

## Local run

    docker build -t ttp-credential-gate:dev .
    docker run --rm -d --name ttp-credential-gate -p 127.0.0.1:8080:8080 ttp-credential-gate:dev
    curl -fsS http://127.0.0.1:8080/healthz
    docker inspect --format '{{.State.Health.Status}}' ttp-credential-gate

Visit http://127.0.0.1:8080/. In a platform instance, connect to target port 8080 through AttackBox. Never expose a deliberately vulnerable service to the public internet.

The app uses Python standard-library HTTP handling and **real SQLite**, random account password digests, server-side opaque sessions, and a non-root Linux service user. The vulnerable query is the actual authentication query; it does not match special payload strings to fake an exploit.

## Static Flag

The file at flags/flag.txt is copied into the image; the app reads it only for an admin-only CSV report. **The value committed to Git is a public DEMO flag**, not a production secret. Do not publish an actual challenge using a static answer exposed in a public repository. Before release, arrange how the final private flag and platform quiz answer are safely provisioned. This exercise intentionally does not change Worker or the existing static-quiz system.

## Verification

    python3 -m unittest discover -s tests -v
    python3 -m py_compile app.py

Tests cover failed login, real SQLi bypass, protected CSV export, auth redirect, malformed SQL error handling, and health check. They require no external Python dependencies. Docker builds and live Worker networking need verification on a Docker-capable runner.

## Files

- app.py: authentic business app with intentionally unsafe SQL
- static/site.css: original interface styling
- flags/flag.txt: replaceable demo static flag
- tests/test_lab.py: regression and exploit acceptance tests
- Dockerfile: single-container, unprivileged process with health check

No SSH, SUID/root, Windows, kernel, or container-escape component. The second machine, Union Ledger, will focus on UNION data extraction, not repeat this login bypass.
