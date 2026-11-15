# Funnel - real-service Docker lab

A single-container recreation of the service chain in the provided **Funnel Write-up**. It uses real vsftpd, OpenSSH and PostgreSQL 15, not fake sockets or simulated services.

## Original path

1. Anonymous FTP on port 21 reveals `mail_backup/welcome_28112022` and `password_policy.pdf`.
2. The message exposes usernames; the policy exposes the default password.
3. `christine` can authenticate over SSH (port 22).
4. PostgreSQL only listens on `127.0.0.1:5432` inside the container.
5. SSH local port forwarding exposes the real database to the attacker's `psql` client.
6. The `secrets` database contains the final `flag` table.

**Flag design:** This box does not have a privilege escalation / root step in the supplied walkthrough. Therefore it has ONE final database flag, not an invented root flag. The flag is authored in `flags/flag.txt` **outside application code** and copied with `COPY flags/flag.txt ...` during build. The entrypoint imports it into PostgreSQL then deletes its temporary plaintext copy.

The FTP email and password-policy PDF are newly recreated teaching materials. They preserve the relevant clues but are not claimed to be original source assets.

## Build

Prerequisites: Docker Engine with Compose plugin.

Change `flags/flag.txt` **before building** to your own single-line value. A rebuild is required when the flag changes:

```sh
docker compose up -d --build
docker compose ps
bash tests/smoke.sh
```

All mapped ports listen on `127.0.0.1` by default to limit exposure to the local machine. For testing from another lab machine, edit Compose port bindings and allow TCP 21, 22, 30000-30009 in an isolated lab network. The FTP passive port range is needed for clients using passive mode; EPSV is recommended behind NAT.

## Guided verification

```sh
# Anonymous FTP (host port 2121). Enter username anonymous, any password if asked.
ftp 127.0.0.1 2121
# cd mail_backup; ls; get welcome_28112022; get password_policy.pdf

# SSH (host port 2222); the password comes from the FTP policy.
ssh -p 2222 christine@127.0.0.1

# In a SECOND terminal, create a local tunnel to the service bound inside container.
ssh -p 2222 -N -L 127.0.0.1:1234:127.0.0.1:5432 christine@127.0.0.1

# Client machine needs postgresql-client installed.
psql -h 127.0.0.1 -p 1234 -U christine -d secrets
# Password from the FTP policy. In psql: SELECT * FROM flag;
```

### Healthcheck

The built-in Docker healthcheck confirms the real FTP and SSH banners, PostgreSQL readiness and the final table's existence. Inspect with:

```sh
docker inspect -f '{{json .State.Health}}' funnel-lab
```

### Multi-stage / image minimization

Stage 1 uses temporary Python to generate the real policy PDF. Stage 2 uses Debian slim with `--no-install-recommends`, contains only runtime packages, and clears APT caches and unneeded documentation. This is not an Alpine mockup: the services actually run. Note PostgreSQL and SSH/FTP make the image larger than a single-process web container.

### Security and fidelity

The weak password and anonymous FTP are intentional. Do not expose this container to public networks. This is a service-misconfiguration lab rather than a software-CVE exploit. The version of vsftpd packaged in Debian may differ from the 3.0.3 version listed by the original write-up; the vulnerable configuration and exploitation sequence are the same. This package has not been Docker-built or end-to-end tested in the creation environment; run `tests/smoke.sh` after building.
