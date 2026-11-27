# Intense — HTB Web-only reconstruction

**Scope:** the Web attack path of the retired HTB Intense machine, independently reconstructed from public writeups. The original private application source is unavailable and is not claimed to be copied.

## Intended path

1. Discover the community message service and public `/src.zip`.
2. Sign in with the disclosed guest account and inspect normal message submission.
3. Use a real SQLite INSERT injection with native error feedback and a conditional `zeroblob()` error oracle to extract the administrator secret.
4. Analyze the custom LWT cookie and exploit SHA-256 secret-prefix MAC length extension. The parser accepts duplicate keys, allowing the appended administrator username and recovered secret to override the guest values.
5. Access the admin log viewer and exploit its unchecked path join to read `/home/analyst/user.txt`.

The original machine continues through SNMP, SSH tunneling and native binary exploitation. Those Linux and binary stages are intentionally excluded from this Web-only Lab. There is one Web Flag and no Root Flag.

## Real components and boundaries

| Component | Runtime |
|---|---|
| Web application | Python 3.12, Flask 3.1.1, Gunicorn 23.0.0 |
| Database | Real SQLite via Python's sqlite3 |
| HTTP | Gunicorn TCP 8080 |
| Web process | Unprivileged `web` account |
| Flag | Random per-instance value at `/home/analyst/user.txt` |

No separate database service, SSH daemon, SNMP agent, compiler or native binary is required. Each real SQLite connection uses a 1 MiB `SQLITE_LIMIT_LENGTH` to preserve the native `SQLITE_TOOBIG` conditional-error signal without attempting a near-gigabyte allocation in the constrained training container. No mock SQL parser, fake error response, test backdoor or simulated command execution is used.

## Build and run

Generate a versioned Flag and matching Challenge answer:

```bash
python3 scripts/generate_intense_release.py --version 0.1.0
docker build -t ttp-intense:local -f labs/intense/Dockerfile labs/intense
docker run -d --name intense-lab \
  --security-opt no-new-privileges \
  --memory 256m --cpus 1 --pids-limit 128 \
  -e INTENSE_WEB_FLAG="$(cat labs/intense/flags/user.txt)" \
  -p 127.0.0.1:8080:8080 ttp-intense:local
```

Login account: `guest / guest`.

Re-running the generator with the same version reuses the existing manifest Flag. A new version generates a new Flag. The LWT signing secret is separately randomized on each container start.

## Independent player and CI

- `exploit.py`: standalone HTTP attacker; performs source review, guest login, SQLite conditional-error extraction, SHA-256 length extension, admin session verification and final log path traversal.
- `writeup.md`: reconnaissance-to-Flag walkthrough.
- `.github/workflows/intense-e2e.yml`: builds the real target, runs the independent attacker over an internal Docker network and checks the exact random Flag.
- `.github/workflows/intense-release.yml`: verifies a versioned release by running the same real attack path before committing the release artifacts.

The attacker never mounts the target filesystem, uses the Docker socket, or invokes `docker exec`. A successful build or healthcheck alone is not an E2E pass. Do not expose this intentionally vulnerable target to the public Internet.
