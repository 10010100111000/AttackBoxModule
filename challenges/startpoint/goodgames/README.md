# GoodGames Lab (SQLi + Flask/Jinja2 SSTI)

This is a deliberately vulnerable, isolated training lab based on the supplied GoodGames write-up. It reproduces the first part of the chain only:

1. Game Warrior static gaming front end with a login modal.
2. SQL injection in the main-site login query.
3. SQLite `main.user` table containing a weak MD5 password hash.
4. Internal administration host using the open-source Volt Flask/Jinja UI.
5. Administrator profile update that stores a name and later compiles it with `render_template_string`, creating stored Jinja2 SSTI.
6. The web process runs as the unprivileged `augustus` user. There is one `user.txt` flag and no container escape/root flag.

## Important safety notes

- This app intentionally contains SQL injection and server-side template injection with command execution inside the application container.
- Compose binds the service to `127.0.0.1:8080`, not to all public interfaces.
- Do not remove `read_only`, `cap_drop`, `no-new-privileges`, or the non-root runtime user unless you understand the isolation impact.
- Do not mount the Docker socket, host home directory, or host root filesystem.
- Use only in an isolated lab environment. Do not expose it directly to the Internet.

## Front-end sources

- Main site: the user-provided Game Warrior HTML template. Its Colorlib attribution comment is retained.
- Admin UI: the open-source AppSeed Flask/Jinja Volt starter, pinned to commit `53c8718aeade16f0058c8bcaac2bc1bee1dbffbf`; the Docker build fetches its original Volt CSS, Bootstrap/Popper assets, and upstream layout templates. Themesberg/AppSeed attribution is retained. See:
  - https://github.com/app-generator/jinja-volt-dashboard
  - https://appseed.gitbook.io/docs/products/jinja-templates/volt-bootstrap-5
  - https://themesberg.com/licensing

The Volt source is fetched during the first Docker build, so the build host needs outbound access to GitHub. No Git client or upstream source checkout is included in the final runtime image.

## Build and run

```bash
docker compose up -d --build
docker compose ps
```

The container listens on port 5000 internally and is published only on the server loopback at `127.0.0.1:8080`.

To access from your workstation, create an SSH tunnel:

```bash
ssh -L 8080:127.0.0.1:8080 your-user@your-linux-server
```

On your workstation, add this hosts entry:

```text
127.0.0.1 goodgames.htb internal-administration.goodgames.htb
```

Then browse:

- http://goodgames.htb:8080/
- http://internal-administration.goodgames.htb:8080/login

## Seeded lab data

Main-site account:

- Email: `admin@goodgames.htb`
- Password hash in `main.user`: MD5 of `superadministrator`

Internal administration login (the password is intended to be recovered from the dumped hash):

- Username: `admin`
- Password: `superadministrator`

A second ordinary account is seeded to make the user table enumeration more realistic.

## Attack path to verify

1. Open the Game Warrior login modal.
2. Capture the POST `/login` request and test the `email` parameter. The server-side SQL query is intentionally concatenated and vulnerable.
3. Enumerate SQLite `main.user` with SQLMap and recover the administrator MD5 hash.
4. Crack the weak hash to recover the reused admin password.
5. Visit the internal administration hostname and sign in.
6. Open User Settings and submit `{{7*7}}`. After redirect, the Username field should display `49`.
7. In the authorized lab only, a Jinja2 SSTI payload can execute commands as the unprivileged `augustus` process inside this container.
8. Read `/home/augustus/user.txt` after obtaining that foothold.

## Flag handling

Edit `flags/user.txt` before building. Dockerfile copies it to `/home/augustus/user.txt` and sets owner `augustus:augustus` with mode `0400`. It is not stored in the Python source. Rebuild the image after changing the flag:

```bash
docker compose build --no-cache
docker compose up -d
```

There is intentionally no `root.txt`: the container escape / host privilege-escalation stage was explicitly excluded from this version.

## Health check and logs

```bash
curl -fsS http://127.0.0.1:8080/healthz
docker inspect --format '{{.State.Health.Status}}' goodgames-lab
docker logs --tail=100 goodgames-lab
bash tests/smoke.sh
```

Health endpoint checks both Flask and SQLite. Docker `HEALTHCHECK` marks the container unhealthy if the web app or database is unavailable.

## Reset

```bash
docker compose down -v
docker compose up -d --build
```

Removing the named volume resets the SQLite database to the seeded state.
