# PG Pebbles — original-stack Docker reconstruction

> **Original exploit chain CI-validated; not an official OffSec image.** The optimized multi-stage image from PR #3 is already merged into main. Historical GitHub CI proves the original ZoneMinder SQLi, database file write and UDF execution path in isolated Docker; it does not prove live Worker deployment or sustained multi-user capacity.

## Design objective

Do not put SQLi on the public login page. Preserve original reconnaissance: the player first sees a straightforward PHP login on port 80, an ordinary Apache default page on port 3305 and a Tomcat service on 8080, then discovers authentic ZoneMinder 1.29.0 through directory enumeration under `/zm/` on **either Apache listener (80 or 3305)**. The landing page does not link to that path. This is CVE-2016-10204 in the **original upstream ZoneMinder PHP code**, not a simulated endpoint.

| Port | Service | Role in enumeration |
| --- | --- | --- |
| 21 | Real vsftpd, Xenial | FTP enumeration; anonymous login disabled |
| 22 | Real OpenSSH, Xenial | SSH fingerprint and possible dead end |
| 80 | Apache 2.4.18 + PHP 7.0 | Pebbles PHP login (behavioral approximation; no SQLi) |
| 3305 | Apache 2.4.18 + PHP 7.0 | Ubuntu default page; original `/zm/` ZoneMinder interface |
| 8080 | Native Tomcat 9.0.30 listener (not Apache) | Nonessential HTTP route, matching original discovery |
| 3306 | MySQL 5.7 on `127.0.0.1` | Original dangerous database privilege boundary |

Source packages come from the Ubuntu 16.04 historical archive; ZoneMinder is pinned to **`1.29.0+dfsg-1ubuntu2`**. Tomcat is downloaded from the Apache archive with a pinned SHA-512. The Ubuntu package supplies the genuine ZoneMinder HTML/CSS/JS and `web/ajax/log.php`.

## Challenge

The Lab has one learner-facing Challenge: [Camera Database](../../challenges/sql-injection/08-camera-database/pebbles.md). Pebbles has one original final target, `/root/proof.txt`; no separate User Flag stage is invented. The Challenge answer must match the private static Root Flag injected at runtime. The repository value is a public demo seed only.

Detailed discovery and exploitation notes are in [writeup.md](writeup.md).

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
Apache default page and native Tomcat, can enumerate the unlinked ZoneMinder installation at **80/zm/** and **3305/zm/**,
matching multiple independent PG writeups. It also verifies MySQL and Tomcat's AJP connector are not
externally reachable.

Run on a dedicated Docker-capable test host:

```bash
bash tests/remote-recon.sh ttp-pebbles:ci
```

No public port forwarding is used, and the probe needs only Python's standard library.

## Static Flag

The original end goal is the root proof. `flags/root.txt` is copied into `/root/proof.txt` with restrictive permissions. **The repository contains only a public demonstration value**, not an actual production answer. Before release, provide a private static flag through the existing Worker **runtime environment** and set the same answer in the platform `quiz.answer`; do not leak the real value through Git or the public GHCR image.

### Provisioning a private static Flag with the existing Worker

The image retains a public **demo** flag for CI. For real challenges, keep the correct static
answer out of GitHub and the public GHCR image. In the target's existing Worker/admin
**environment variables**, set:

```text
PEBBLES_REQUIRE_STATIC_FLAG=1
PEBBLES_STATIC_ROOT_FLAG=<your privately chosen, fixed Flag>
```

Use the **same static value** in the challenge's `quiz.answer`. The entrypoint writes
it to `/root/proof.txt` before starting the vulnerable services and keeps mode 0600.
With `PEBBLES_REQUIRE_STATIC_FLAG=1`, the container refuses to start if the real
Flag is missing. This **does not use dynamic Flag rotation** or modify Worker internals.
Admin access to Docker inspection can reveal container environment variables, so
restrict Docker API/Worker administrative access.

CI additionally checks that the same private override works across fresh instances, remains unreadable to
`www-data`, and that a required-but-missing Flag fails closed.

## Runtime constraints

One challenge = one Docker image = one per-user target container, as supported by the existing AttackBox Worker. All original processes share an isolated network namespace; MySQL listens only on container loopback and deliberately runs as **container UID 0** to reproduce the original unsafe UDF escalation. This is not host root.

An earlier GitHub CI resource sample measured **414.7 MiB and ~102 PIDs** with the Worker default 512 MiB / 256 PIDs and one CPU. That was healthy but leaves little headroom. Start production Worker trials with **1024 MiB and 256 PIDs**, then measure sustained usage and adjust; this is a provisional recommendation, not a proven capacity requirement.

The Pebbles 80/tcp page was not released in the reviewed public sources, so that custom landing page is only an approximate behavioral reconstruction. The actual ZoneMinder web frontend is installed unmodified from the original Ubuntu package.

## Lean runtime build and measured disk usage

The Dockerfile uses **three actual stages**:

1. `tomcat-artifact` (Alpine only for artifact download, verifying upstream SHA-512);
2. `xenial-assembled` (Ubuntu 16.04 installs and configures genuine old PHP 7, Apache, MySQL 5.7, ZoneMinder 1.29.0, OpenSSH, vsftpd, Java 8 and original Tomcat);
3. `optimized-runtime` (`FROM scratch` copies the completed **Ubuntu** filesystem and reinstates ENV, entrypoint, ports and healthcheck). This is **not** an Alpine or musl runtime; the old Ubuntu userspace and glibc remain.

An InnoDB redo-log configuration is applied **before** MySQL's package initialization, creating two **8 MiB** redo logs in the shared image, rather than default 48 MiB logs. These are real MySQL 5.7 files, not placeholders, and the full SQLi and UDF chain is verified in Docker.

| CI result | Prior image | Optimized image |
| --- | ---: | ---: |
| Local Docker image size | 228.6 MiB | **220.7 MiB** |
| MySQL initialized data directory | approximately 122 MiB | **approximately 42 MiB** |
| Worker 512 MiB memory profile | Healthy, approximately 390 MiB | Healthy, approximately 394 MiB |
| Original ports, SQLi, UDF, static Flag and per-user reset | Pass | Pass |

CI comparison: https://github.com/10010100111000/AttackBoxModule/actions/runs/44946865137

**Trade-off:** A non-squashed Ubuntu-based image with the smaller redo logs is approximately **228.5 MiB**, whereas the final scratch-repacked image is **220.7 MiB**. The latter saves about 7.8 MiB as an individual image, but it does **not** share the original Ubuntu parent layers with other images. When running many different Xenial labs on one VPS, total disk usage across all images may favor the layered alternative. The directory-size reduction and the `docker image inspect .Size` reduction are different measurements and should not be confused.

The real Java 8/Tomcat and ZoneMinder/MySQL components were not removed just to obtain a smaller size. The production Worker and sustained concurrent-user memory still need verification.

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
- Docker build, runtime, real ZoneMinder SQLi → PHP and UDF Root: **passed in the original-stack CI and the three-stage size-comparison CI**.
- Attacker-side reconnaissance, independent instance reset and private static Flag provisioning: **historical CI evidence exists**; this Lab has not yet been migrated to the current unified E2E workflow.
- Real Worker deployment and sustained concurrent-user capacity: **not verified and outside this Lab-content task**.

Do not describe the historical CI as a current unified E2E pass. Keep the current `e2e_ci_status` pending until a current-standard attacker workflow is actually run. Production answers must use the private runtime Flag override, not the demo seed.
