# Devvortex - single-container training lab

This is a **deliberately vulnerable, local-only** reproduction project based on the supplied HTB Devvortex write-up (2023). It is not an official HTB image. Never expose it to the Internet.

## Architecture

One Ubuntu 22.04 container runs: nginx :80, PHP 8.1-FPM, **real Joomla 4.2.6**, MariaDB bound to 127.0.0.1, and sshd :22. The Docker health check checks the main website, Joomla admin endpoint, MariaDB, and SSH banner. Initial Joomla installation occurs automatically on the first container start. It can take longer than subsequent starts.

**Two separate virtual hosts:** `devvortex.htb` is a static landing site; `dev.devvortex.htb` is Joomla. Both are served over the *same* HTTP port via the Host header. For local use add the domains to your hosts file if desired.

## Start

```bash
docker compose up -d --build
# or
docker build -t devvortex-lab .
docker run --rm -d --name devvortex-lab -p 127.0.0.1:8080:80 -p 127.0.0.1:2222:22 devvortex-lab
```

Linux/macOS hosts:

```bash
echo '127.0.0.1 devvortex.htb dev.devvortex.htb' | sudo tee -a /etc/hosts
```

Windows: edit `%SystemRoot%\System32\drivers\etc\hosts` as administrator and add the same entry.

Sites: `http://devvortex.htb:8080/` and `http://dev.devvortex.htb:8080/`.

Alternatively without hosts modification:

```bash
curl -H 'Host: devvortex.htb' http://127.0.0.1:8080/
curl -H 'Host: dev.devvortex.htb' http://127.0.0.1:8080/administrator/
```

## Health and acceptance checks

```bash
docker ps
docker inspect --format '{{json .State.Health}}' devvortex-lab
docker logs -f devvortex-lab
bash tests/smoke.sh
```

The test asserts: landing page, Joomla 4.2.6 version XML, administrator interface, and the information disclosure endpoint exposing the *lab's* configured password. Because the image has not been built in this authoring environment, treat the test as acceptance criteria, not proof of success.

## Intended lab chain

1. Discover `dev.devvortex.htb` by Host-header vhost enumeration. It runs Joomla **4.2.6**.
2. The real (old) Joomla `/api/index.php/v1/config/application?public=true` endpoint is intended to demonstrate **CVE-2023-23752**. Discover the Joomla config credential in the response.
3. Authenticate to `/administrator` and edit the Cassiopeia template `error.php` using the normal Joomla admin template editor; PHP executes as `www-data`.
4. MariaDB database `joomla`, table `sd4fg_users`: there is a second Joomla user `logan` with a bcrypt password hash. For repeatable local training, the SSH password of `logan` matches the PDF example. SSH is mapped to host port 2222.
5. User `logan` may run the **genuine historical Ubuntu** `/usr/bin/apport-cli` as root with sudo, installed from Ubuntu's official archived version `2.20.11-0ubuntu82`. This predates the fixed Jammy version `2.20.11-0ubuntu82.4` (CVE-2023-1326). No wrapper or substitute pager is installed. Interactive pager-based escalation requires a suitable report/terminal and has **not** been tested end to end here.
6. Training flags exist in `/home/logan/user.txt` and `/root/root.txt`; these are *not* the original HTB flags.

## Verify the *actual* Apport installation

After starting the container, run:

```bash
docker exec devvortex-lab bash /usr/local/bin/check-apport.sh
docker exec devvortex-lab dpkg-query -W apport python3-apport python3-problem-report
docker exec devvortex-lab sudo -l -U logan
```

All three packages must be exactly `2.20.11-0ubuntu82`. Ubuntu fixed CVE-2023-1326 in `2.20.11-0ubuntu82.4` for 22.04. Merely observing the old package versions does **not** prove the interactive exploit succeeds: verify that separately with an actual TTY and crash report. Do not use the lab outside an isolated VM.

## Build dependencies, caveats and fidelity

- During image **build**, the Dockerfile downloads the genuine April 2022 Ubuntu Apport `.deb` archives, refuses unexpected package versions and holds the packages against future updates. It also downloads the **official Joomla 4.2.6 Full Package** and checks its published MD5 (`e01705da3de1a541d2b3c07791968e01`). The official download URL and distro APT mirrors must be reachable **by the Docker host at build time**. No Joomla binary is embedded in this ZIP.
- A clean container initializes MariaDB, installs Joomla via Joomla's `installation/joomla.php install` command, and inserts a second Joomla user. This uses real Joomla database structures, not a stubbed JSON API.
- Restarting the **same** container retains state. Removing/recreating it without persisting `/var/lib/mysql` and the Joomla site resets the lab. This is deliberate for an ephemeral challenge image.
- The landing page is an original minimalist reproduction, not a pixel-perfect copy of HTB's site.
- This environment could not execute a `docker build` or reach Joomla's download endpoint; neither the exploit chain nor container startup has been end-to-end verified. Use the smoke test and logs above. In particular, an installer command or old endpoint behavior may require adjustment if upstream packaging differs.
- Host ports are restricted to `127.0.0.1` by default. Do not publish vulnerable HTTP or SSH services on a public interface. Run on an isolated machine/VM, not a production host.

## Remove

```bash
docker compose down
# or docker rm -f devvortex-lab
```

## Files

- `Dockerfile`: all OS services and official Joomla package
- `config/nginx.conf`: name-based vhosts and FastCGI
- `scripts/start.sh`: MariaDB bootstrap, Joomla CLI installation, Joomla user seed, PHP-FPM/nginx/SSH processes
- `scripts/healthcheck.sh`: Docker HEALTHCHECK
- `tests/check-apport.sh`: verifies the real pinned Ubuntu Apport versions and sudo rule
- `tests/smoke.sh`: HTTP regression / CVE acceptance check
- `compose.yaml`: single-service, local-only launch

## Multi-stage image size optimizations

The Dockerfile uses **two stages**:

1. `artifacts` downloads and verifies the official Joomla 4.2.6 archive and the historical Ubuntu Apport `.deb` packages, then extracts Joomla. This entire stage is **not included** in the final runtime image.
2. `runtime` installs required OS services with `--no-install-recommends`, installs the actual old Apport packages, retains the real Joomla installation, and removes APT lists, `.deb` files, download caches, package logs, manual pages and documentation. No curl/tar download archive is retained from the builder.

The final stage deliberately uses **Ubuntu 22.04**, not Alpine or `scratch`: this challenge needs real Ubuntu Apport binaries and their dependencies, a working PHP/Joomla installation, SSH, and MariaDB. Using an incompatible minimal distribution would sacrifice exploit fidelity. In a single-container lab, MariaDB and the required daemons dominate the unavoidable size.

Build and inspect the resulting size:

```bash
docker build --pull -t devvortex-lab:optimized .
docker image inspect devvortex-lab:optimized --format '{{.Size}} bytes'
docker history --no-trunc devvortex-lab:optimized
```

Compare the size and functionality against the earlier image if both are available. **Image size has not been measured here:** no Docker daemon is available in this authoring environment. The new stages and cleanup reduce unnecessary artifacts, but the final size and complete exploit chain must be validated by running the image.

Avoid `docker image prune -a` while other projects depend on their cached images. BuildKit's disposable build-stage layers can be reclaimed independently using `docker builder prune` when appropriate.
