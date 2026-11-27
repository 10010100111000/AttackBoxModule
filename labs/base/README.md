# Base — PHP 7.2 authentication bypass and upload lab

This Lab preserves the original Base two-stage attack path using the real PHP 7.2 runtime and standard Linux services.

## Attack path

1. Enumerate Apache and discover the listable /login/ directory.
2. Recover the login implementation fragments from the exposed Vim login.php.swp.
3. Exploit PHP 7.2 strcmp(array, string) warning/NULL behavior combined with loose == 0 comparison.
4. Reach the authenticated upload page and upload a real PHP file through the application.
5. Execute commands as Apache's www-data user.
6. Read the application configuration and discover credentials reused by local user john.
7. Authenticate to the real OpenSSH service and retrieve the User Flag.
8. Abuse the actual sudo permission for GNU find to execute a command as root and retrieve the Root Flag.

This is not a Web-only Lab: the intended source includes a real SSH pivot and local sudo privilege escalation, so both User and Root Flags are retained.

## Runtime

- PHP 7.2 Apache image (required for the legacy strcmp behavior)
- Apache directory listing enabled for the intended discovery path
- OpenSSH server for the credential-reuse stage
- john account with the intended password reuse
- sudo permission limited to /usr/bin/find
- Separate User and Root Flag files copied into their intended locations

## Build and run

    docker build --pull -t ttp-base .
    docker run --rm -d --name ttp-base -p 127.0.0.1:8080:80 -p 127.0.0.1:2222:22 ttp-base

Browse to http://127.0.0.1:8080/. The login page is linked from the public landing page.

Do not expose this intentionally vulnerable image to a public network. Run it only in an isolated training environment.

## Flags

scripts/generate_base_release.py --version 0.1.0 generates two independent random Flags and synchronizes:

- labs/base/user_flag.txt
- labs/base/root_flag.txt
- labs/base/flags/releases/0.1.0.json
- the two quiz answers in challenges/startpoint/base/Base.md

Re-running the same version reuses its manifest values. A new version generates a new pair. The Dockerfile copies the User Flag to /home/john/user.txt and the Root Flag to /root/root.txt with their intended ownership and permissions.

## Automated acceptance

- exploit.py: independent HTTP + SSH attacker; it follows the actual chain and retrieves both Flags.
- tests/Dockerfile: minimal attacker image containing the OpenSSH client and sshpass.
- .github/workflows/base-e2e.yml: builds the real target, starts it on a private Docker network and verifies both Flags through the expected path.
- .github/workflows/base-release.yml: versioned release that must pass the same exploit before committing generated Flag artifacts.

The attacker never mounts the target filesystem, uses the Docker socket or calls docker exec to obtain a Flag.
