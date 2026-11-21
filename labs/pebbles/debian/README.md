# PG Pebbles — Debian Jessie-only runtime experiment

> **Status: Docker end-to-end CI passed. Not for public deployment and not merged into main.** Test branch: `test/pebbles-debian-runtime`, Draft PR #4.

## Runtime and provenance

This is a **real Debian userspace**, not a renamed or repacked Ubuntu filesystem:

| Layer / Component | Version | Source |
| --- | --- | --- |
| Base OS | Debian 8 Jessie Slim | `debian/eol:jessie-slim` |
| Surveillance application | ZoneMinder `1.29.0+dfsg-1~bpo8+1` | Historical Debian Jessie Backports binary package |
| Database | Oracle MySQL Community Server **5.7.30** | Original Debian 8 `.deb` files with SHA-256 checksums pinned in `mysql-5.7.30.sha256` |
| Web service | Apache + **PHP 5.6** | Debian Jessie |
| Java/Tomcat | OpenJDK 8 + original Tomcat **9.0.30** | Debian Jessie Backports + Apache Software Foundation SHA-512-verified archive |
| Other services | vsftpd, OpenSSH | Debian Jessie |

`alpine:3.20` is used **only as an artifact downloading stage** for MySQL and Tomcat; the final runtime contains no Alpine or Ubuntu userspace.

**Documented fidelity difference:** OffSec PG Pebbles was observed running Ubuntu 16.04 + PHP 7.0, whereas this experiment intentionally uses Debian Jessie + PHP 5.6 to install the original Debian ZoneMinder 1.29.0 binary. The authentic `CVE-2016-10204` SQLi, file-write pathway and root-running MySQL/UDF behavior are tested rather than merely inferred from version strings. The port 80 login is a functional approximation, not original unreleased OffSec source code.

## Build and tests

From the repository root, only on an isolated Docker-capable machine:

```bash
docker build -f labs/pebbles/Dockerfile.debian -t ttp-pebbles:debian-test labs/pebbles
bash labs/pebbles/debian/tests/full-acceptance.sh ttp-pebbles:debian-test
bash labs/pebbles/debian/tests/remote-recon.sh ttp-pebbles:debian-test
bash labs/pebbles/tests/static-flag-acceptance.sh ttp-pebbles:debian-test
bash labs/pebbles/tests/reset-acceptance.sh ttp-pebbles:debian-test
```

CI also builds `Dockerfile.debian-probe` to confirm the historical package dependencies, validates the exact vulnerable upstream source and starts the actual multi-service runtime. UDF test helper is built in a **separate CI-only image**; it is not copied into the challenge target as a fake exploit.

**Latest tested commit:** `a1079e3f38c729b130e2bcd88e77f8be6901180a`. All CI steps passed:
https://github.com/10010100111000/AttackBoxModule/actions/runs/44952051499

## Measured size

`docker image inspect -f '{{.Size}}'` on Linux amd64 CI runner:

| Variant | Measured image size | Meaning |
| --- | ---: | --- |
| Existing validated Ubuntu 16.04 3-stage release | **220.7 MiB** | Baseline already merged into `main` |
| Debian Jessie candidate before optional documentation filtering | **232.7 MiB** (243,981,496 bytes) | All functional CI checks passed |
| Debian Jessie candidate after filtering manpages, locales, etc. | **232.7 MiB** (243,982,135 bytes) | All functional CI checks passed; no meaningful improvement |

The Debian image is approximately **12 MiB larger**, not smaller. Its installed MySQL data directory is approximately **42 MiB**, Java runtime **115 MiB**, and ZoneMinder web/application tree **18 MiB** (directory disk usage and Docker image size are distinct measurements). Merely switching the OS base is therefore **not** an effective size optimization for Pebbles.

Debian variant may still be useful as a genuinely non-Ubuntu alternative, but does not yet justify replacing the smaller, closer-to-original Ubuntu 16.04 image. The experiment is deliberately **not promoted** to the canonical `labs/pebbles/Dockerfile`; no GHCR publishing is requested. Keep the static Flag/Worker interface unchanged.

## Sources

- Debian EOL images: https://hub.docker.com/r/debian/eol/tags
- Debian 1.29.0 source: https://sources.debian.org/src/zoneminder/1.29.0%2Bdfsg-1~bpo8%2B1/
- Oracle historical MySQL APT archive: https://repo.mysql.com/apt/debian/dists/jessie/mysql-5.7/binary-amd64/Packages
- Apache Tomcat 9.0.30: https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.30/
