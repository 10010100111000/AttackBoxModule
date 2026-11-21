# PG Pebbles — original-stack Docker reconstruction

> **Unverified implementation candidate — NOT a finished / published machine.** The GitHub PR stays in draft until a clean image build and real exploitation tests pass. This is an independent recreation, not an official OffSec image or a copy of non-public OffSec assets.

## Design objective

Do not put SQLi on the public login page. Preserve original reconnaissance: the player first sees a straightforward PHP login on port 80, an ordinary Apache default page on port 3305 and a Tomcat service on 8080, then discovers authentic ZoneMinder 1.29.0 at `/zm/`. This is CVE-2016-10204 in the **original upstream ZoneMinder PHP code**, not a simulated endpoint.

| Port | Service | Role in enumeration |
| --- | --- | --- |
| 21 | Real vsftpd, Xenial | FTP enumeration; anonymous login disabled |
| 22 | Real OpenSSH, Xenial | SSH fingerprint and possible dead end |
| 80 | Apache 2.4.18 + PHP 7.0 | Pebbles PHP login (behavioral approximation; no SQLi) |
| 3305 | Apache 2.4.18 + PHP 7.0 | Ubuntu default page; original `/zm/` ZoneMinder interface |
| 8080 | Native Tomcat 9.0.30 listener (not Apache) | Nonessential HTTP route, matching original discovery |
| 3306 | MySQL 5.7 on `127.0.0.1` | Original dangerous database privilege boundary |

Source packages come from the Ubuntu 16.04 historical archive; ZoneMinder is pinned to **`1.29.0+dfsg-1ubuntu2`**. Tomcat is downloaded from the Apache archive with a pinned SHA-512. The Ubuntu package supplies the genuine ZoneMinder HTML/CSS/JS and `web/ajax/log.php`.

## Build and local testing

Only in an isolated lab Docker host. **Never expose this image directly to the public Internet.** No privileged containers, host Docker socket or host root mounts.

```bash
cd labs/pebbles
docker build --pull -t ttp-pebbles:dev .
docker run --rm -d --name pebbles-local --memory 1536m --pids-limit 512 \
  -p 127.0.0.1:8081:80 -p 127.0.0.1:3305:3305 \
  -p 127.0.0.1:8080:8080 ttp-pebbles:dev
curl http://127.0.0.1:8081/
curl http://127.0.0.1:3305/zm/index.php
docker inspect --format '{{.State.Health.Status}}' pebbles-local
```

For deterministic tests in an **isolated `--network none` container**, run:

```bash
PEBBLES_TEST_SQLI=1 bash tests/service-smoke.sh ttp-pebbles:dev
```

The acceptance script must verify the actual vulnerable ZoneMinder log query writes a PHP marker via MySQL `INTO OUTFILE` and that Apache executes it. This cannot be replaced by a synthetic route or by merely checking the CVE version number. A separate UDF execution proof as container root is still required for the final Root stage.

## Real attacker-side reconnaissance acceptance

The original-stack test validates internal services and the genuine SQL injection and root chain.
A separate `tests/remote-recon.sh` launches **two containers on an isolated Docker internal
bridge**. It checks that an attacker sees the original five TCP services, identifies the
Apache default page and native Tomcat, can enumerate ZoneMinder at **3305/zm/**, and **cannot
access /zm/ on the 80/tcp decoy**. It also verifies MySQL and Tomcat's AJP connector are not
externally reachable.

Run on a dedicated Docker-capable test host:

```bash
bash tests/remote-recon.sh ttp-pebbles:ci
```

No public port forwarding is used, and the probe needs only Python's standard library.

## Static Flag

The original end goal is the root proof. `flags/root.txt` is copied into `/root/proof.txt` with restrictive permissions. **The repository contains only a public demonstration value**, not an actual production answer. Before release, inject a privately managed static flag during the build and set the same answer in the platform `quiz.answer`; do not leak the real value through Git.

## Runtime constraints

One challenge = one Docker image = one per-user target container, as supported by the existing AttackBox Worker. All original processes share an isolated network namespace; MySQL listens only on container loopback and deliberately runs as **container UID 0** to reproduce the original unsafe UDF escalation. This is not host root.

An earlier GitHub CI resource sample measured **414.7 MiB and ~102 PIDs** with the Worker default 512 MiB / 256 PIDs and one CPU. That was healthy but leaves little headroom. Start production Worker trials with **1024 MiB and 256 PIDs**, then measure sustained usage and adjust; this is a provisional recommendation, not a proven capacity requirement.

The Pebbles 80/tcp page was not released in the reviewed public sources, so that custom landing page is only an approximate behavioral reconstruction. The actual ZoneMinder web frontend is installed unmodified from the original Ubuntu package.

## Sources

- Full PG research and known deviations: [RECONSTRUCTION.md](RECONSTRUCTION.md)
- Real historical ZoneMinder: https://github.com/ZoneMinder/zoneminder/tree/v1.29.0
- Old Ubuntu install: https://wiki.zoneminder.com/Ubuntu_Server_16.04_64-bit_with_Zoneminder_1.29.0_the_easy_way
- Actual SQLi: https://ubuntu.com/security/CVE-2016-10204
- Independent PG writeup: https://www.juannemina.com/writeups/pebbles-proving-grounds/
- Original port scan: https://walkthroughs.cyanidesecurity.com/proving-grounds/pebbles
- Apache Tomcat SHA-512: https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.30/bin/apache-tomcat-9.0.30.tar.gz.sha512

## Acceptance status

- Real upstream ZoneMinder `limit` SQL concatenation: **source verified**.
- PHP entry page: **local HTTP tests passed**.
- Docker build, runtime, real ZoneMinder SQLi → PHP and UDF Root: **passed in GitHub CI on an earlier revision**, pending successful checks on this branch head.
- Attacker-side port reconnaissance, access restrictions, real Worker, and reset: **new remote regression test added; latest result pending**.

**Do not register or publish until all tests pass.**
