# Shocker — authentic GNU Bash 4.3 / Apache CGI Shellshock

An independent Linux Docker reconstruction of the retired HTB Shocker machine. Not an official HTB image; the original HTB landing-page artwork/source is not claimed to be reproduced.

## Real vulnerable components

- GNU Bash 4.3, built from the official upstream tarball with SHA-256 verification; the vulnerable pre-patch environment-function parser is retained.
- Apache native CGI (mod_cgi) executes the actual user.sh script using Bash 4.3. No custom header parser or simulated Shellshock handler exists.
- Apache/CGI runs as the unprivileged shelly account.
- Native sudoers permits shelly to execute /usr/bin/perl as root without a password.

## Player path

1. Inspect the simple landing page and enumerate the unlinked CGI directory.
2. Identify the uptime CGI script and understand which interpreter executes it.
3. Exploit the original Bash 4.3 Shellshock environment-variable parsing behavior to execute as shelly.
4. Retrieve the User Flag.
5. Inspect the actual sudo permission and use the permitted Perl interpreter to retrieve the Root Flag.

## Build

From the repository root:

~~~sh
docker build -f labs/shocker/Dockerfile -t ttp-shocker:dev labs/shocker
docker run -d --name shocker --network none --memory 96m --pids-limit 96 ttp-shocker:dev
docker inspect -f '{{.State.Health.Status}}' shocker
~~~

The image keeps the original vulnerable Bash binary and Apache CGI behavior. It does not include a fake command endpoint, privileged mode, host networking or a Docker socket.

## Flags

Default files are development seeds only: /home/shelly/user.txt and /root/root.txt. For an isolated instance, inject SHOCKER_STATIC_USER_FLAG, SHOCKER_STATIC_ROOT_FLAG and SHOCKER_REQUIRE_PRIVATE_FLAGS=1. The entrypoint writes the values with deliberate ownership/permissions and removes the variables before launching the services.

## Automated acceptance

The dedicated workflow .github/workflows/shocker-e2e.yml builds the target and a separate non-root HTTP attacker, then runs the complete Shellshock -> User Flag -> sudo Perl -> Root Flag path against one clean instance on an internal-only Docker network. The CI creates one random User Flag and one random Root Flag for that run and checks their exact values through the real CGI exploit. It does not start a second target instance.

The Lab E2E is separate from Worker lifecycle, platform scheduling and backend grading.
