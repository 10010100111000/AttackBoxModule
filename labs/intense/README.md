# Intense — HTB Web-only reconstruction

**Status:** initial implementation on a feature branch; not yet built, manually accepted, Worker-verified or released. This is an independent reconstruction of the retired HTB Intense Web path, not the original private source or VM.

## Scope and design decision

The Web path is retained in its original order:

1. Discover the public community message application and its downloadable source archive.
2. Sign in with the disclosed guest account and inspect the message submission behavior.
3. Exploit a real SQLite INSERT injection. The application returns SQLite errors directly; a conditional SQL expression distinguishes a successful insert from a genuine SQLite error, allowing extraction of the administrator's stored secret.
4. Analyze the custom LWT cookie. Its SHA256(secret || message) construction is vulnerable to a SHA-256 length-extension attack. The parser accepts duplicate keys and later username=admin / administrator secret values override the guest values.
5. Use the resulting administrator session to access the log viewer.
6. Exploit the log viewer's unchecked path join to read the Web goal at /home/analyst/user.txt.

The original machine continues beyond this point through SNMP command execution, SSH tunneling and a custom native binary. Those unrelated Linux / binary exploitation stages are deliberately excluded from this Web-only target.

## What is preserved and what is reconstructed

- Flask and SQLite remain the real application and database technologies.
- The public /src.zip, guest login, 140-character message form, direct SQLite error feedback, conditional error oracle, custom SHA-256 prefix MAC, duplicate-key session parsing, admin log routes and path traversal are preserved as observable behaviors.
- The original private application source is not copied. The route handlers and templates are independently written to preserve the same discovery and exploit path.
- The target does not claim a framework CVE. The SQL injection, weak MAC construction and path traversal are intentional application-level vulnerabilities.
- The UI is a small original community message application, not a pixel-perfect copy of the retired HTB branding.

## Real components

| Component | Runtime |
|---|---|
| Web application | Python 3.12, Flask 3.1.1, Gunicorn 23.0.0 |
| Database | Python's real SQLite library |
| Web listener | Gunicorn on TCP 8080 |
| Flag | Per-instance INTENSE_WEB_FLAG, written to /home/analyst/user.txt at startup |

There is no separate database service, SSH daemon, SNMP agent, compiler, or binary exploitation service.

## Local build and run

    docker build -t ttp-intense:local -f labs/intense/Dockerfile labs/intense

    docker run -d --name intense-lab \
      --security-opt no-new-privileges \
      --memory 256m --cpus 1 --pids-limit 128 \
      -e INTENSE_WEB_FLAG='TTP{replace_with_per_instance_value}' \
      -p 127.0.0.1:8080:8080 ttp-intense:local

    docker inspect -f '{{.State.Health.Status}}' intense-lab

Login account: guest / guest.

The target writes the injected value to a real file readable by the web process. It is not embedded in the image or source archive. Production must supply a unique per-instance value. The local fallback in scripts/start.sh is for smoke use only.

## Security and isolation

- The app runs as the unprivileged web account.
- The SQLite database is local to the container.
- No host mounts, Docker socket, privileged mode, extra Linux capabilities, or external services are required.
- The log traversal can read files visible to the web process; the target flag is deliberately readable to reproduce the original Web objective.
- Do not publish this intentionally vulnerable service to the public Internet.

## Engineering status

- Multi-stage build; only Flask/Gunicorn, Python and curl/su-exec are in the runtime image.
- Healthcheck verifies the actual HTTP health endpoint and a SQLite query.
- CI should perform build, startup, healthcheck and ordinary page smoke checks only. Do not add automated SQLi, hash-extension, authentication bypass or Flag extraction scripts.
- Functional acceptance is limited to ordinary application behavior: homepage and login page render, source archive downloads, the disclosed guest account can sign in, a normal message can be submitted, guest access to the admin page is denied, and the container remains healthy.
- Do not add automated exploit-chain scripts, SQLi payload tests, cookie-forgery tests, or Flag-extraction tests. The purpose of CI is to ensure the target starts and its ordinary application functions work.
- Worker network isolation, per-instance Flag injection and Web backend scoring remain separate deployment checks.

## Public references

- https://www.hackthebox.com/machines/intense
- https://romanh.de/writeup/htb-intense
- https://www.willsroot.io/2020/11/intense-hackthebox-writeup.html
- https://github.com/zweilosec/htb-writeups/blob/master/linux-machines/hard/intense-write-up.md
