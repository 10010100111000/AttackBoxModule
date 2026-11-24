# Zipping — Web-only reconstruction

**Status: implementation pending independent full-chain CI.** This is not an official Hack The Box image or a copy of the unavailable original private source.

## Exploit route and source fidelity

The reconstructed target preserves the observable Web path from the retired HTB Zipping machine:

1. A watch storefront and careers form accept ZIP archives holding a single PDF.
2. Real PHP ZipArchive validates the entry and the native 7z extractor retains Unix symlink metadata. The resulting symlink is moved to the Apache-served uploads directory and can disclose server-side source files.
3. Real PHP source contains the flawed multiline regex check, followed by an unsafe PDO query against real MariaDB.
4. A newline can bypass the regex. Actual UNION SQL injection, a MariaDB account with FILE privilege and an unrestricted secure_file_priv allow writing PHP through SELECT INTO OUTFILE.
5. The existing shop page includes a file ending in .php after file_exists check. Including the database-written file executes code as ordinary www-data, which is the Web-only success target.

No SSH, sudo, Linux root, shared-object injection, or extra Docker Capability is required. There is one Web goal Flag in /home/rektsu/user.txt. A target startup variable ZIPPING_USER_FLAG can replace the development placeholder for a newly created instance. The Worker only schedules and forwards variables, not Flag checks.

The original private PHP source and theme assets are not available. Functionality and vulnerable primitives are reconstructed from publicly verified writeups and official machine synopsis, while product data and visual style are independently authored. No fake parser or simulated file-read endpoint is used.

## Build and local run

```bash
docker build -t ttp-zipping:local -f labs/zipping/Dockerfile labs/zipping
docker run -d --name zipping-local --cap-drop ALL --security-opt no-new-privileges --memory 1g --cpus 1.5 --pids-limit 240 -e ZIPPING_USER_FLAG='TTP{example_web_flag}' -p 127.0.0.1:8080:8080 ttp-zipping:local
docker inspect -f '{{.State.Health.Status}}' zipping-local
```

The image contains real Apache mod_php, MariaDB and 7z in one Debian Bookworm container, with database listening only inside container localhost. No Ubuntu, systemd, Docker socket, host volumes, or special capabilities. Image and memory figures require actual CI measurements.

## Test gate

The separate Python attacker container only communicates through HTTP, builds a true Unix symlink ZIP, reads real PHP source, validates regular SQLi rejection and newline bypass, proves native database FILE write, includes the resulting PHP using the actual LFI and retrieves a per-instance Flag. GitHub Actions should run two fresh isolated targets with different flags. Until all steps are green, this is not a verified playable target and the release block stays.

References:
- https://www.hackthebox.com/machines/zipping
- https://0xdf.gitlab.io/2024/01/13/htb-zipping.html
- https://www.youtube.com/watch?v=C78yku9WC0o
