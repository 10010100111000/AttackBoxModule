# Devvortex — Joomla 4.2.6 Web-only training lab

This is a deliberately vulnerable, local-only reproduction of the Web entry path from HTB Devvortex. It uses the official Joomla 4.2.6 package and the real CVE-2023-23752 configuration disclosure behavior.

## Scope

This platform version is intentionally **Web-only**:

- Host-header virtual-host discovery
- Joomla 4.2.6 version identification
- Unauthenticated configuration disclosure (CVE-2023-23752)
- Joomla Super User login using the disclosed configuration credential
- Cassiopeia template editor and PHP execution as `www-data`
- One Web Flag at `/home/www-data/user.txt`

It does not include SSH, Linux credential pivoting, Apport, container escape or a Root Flag. Those stages belong to the original full Linux machine and are deliberately excluded from this Web curriculum variant.

## Architecture

One Ubuntu 22.04 container runs nginx, PHP 8.1-FPM, MariaDB and the unmodified Joomla 4.2.6 application. MariaDB listens only on loopback. Two HTTP virtual hosts share port 80:

- `devvortex.htb`: small public landing page
- `dev.devvortex.htb`: real Joomla CMS

The official Joomla 4.2.6 archive is downloaded during the disposable build stage and checked against its published MD5 before being copied into the runtime image. The vulnerable endpoint and administrator/template functionality are provided by Joomla itself; no mock API or fake CMS is used.

## Build and run

```bash
docker build --pull -t devvortex-lab .
docker run --rm -d --name devvortex-lab -p 127.0.0.1:8080:80 devvortex-lab
```

For local browser access, add this line to the host's hosts file:

```text
127.0.0.1 devvortex.htb dev.devvortex.htb
```

Then browse to `http://devvortex.htb:8080/` or `http://dev.devvortex.htb:8080/administrator/`.

Do not publish this intentionally vulnerable service to a public interface. Use an isolated machine or private lab network.

## Flag lifecycle

`scripts/generate_devvortex_release.py --version 0.1.0` creates a random Flag and synchronizes it across:

- `labs/devvortex/flags/user.txt`
- `labs/devvortex/flags/releases/0.1.0.json`
- `challenges/startpoint/devvortex/Devvortex.md`

Re-running the same version reuses its manifest Flag. A new version creates a new Flag. The Dockerfile copies the generated file to `/home/www-data/user.txt`, owned by `www-data` with mode `0400`.

## Checks

```bash
docker inspect --format '{{json .State.Health}}' devvortex-lab
bash tests/smoke.sh http://127.0.0.1:8080
```

The Lab-specific workflow `.github/workflows/devvortex-e2e.yml` uses an independent attacker container on an internal Docker network. It performs the actual HTTP disclosure, Joomla administrator login, template-editor save, command execution identity check and exact Flag retrieval. The attacker does not mount the target filesystem, use the Docker socket or call `docker exec`.

A successful image build, healthcheck or ordinary smoke test alone is not a full E2E pass.

## Files

- `Dockerfile`: multi-stage official Joomla download and minimal Web runtime
- `config/nginx.conf`: Host-header virtual hosts and PHP-FPM routing
- `scripts/start.sh`: MariaDB bootstrap, real Joomla schema and user initialization
- `scripts/healthcheck.sh`: nginx, Joomla and MariaDB health
- `tests/smoke.sh`: normal HTTP and Joomla disclosure regression checks
- `exploit.py`: independent network-only player
- `writeup.md`: reconnaissance-to-Flag walkthrough
- `flags/user.txt`: generated Web Flag seed
