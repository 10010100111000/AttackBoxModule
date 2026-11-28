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

User and Root Flags are versioned CI release artifacts baked into the image at /home/shelly/user.txt and /root/root.txt. The entrypoint only validates ownership, format and permissions; it does not accept Flag environment variables or generate new values. Rebuilding the same version preserves the same pair; a new release version rotates both Flags and synchronizes the three Challenge answers.

## Challenge reuse

Three learner-facing Challenges reuse this one Lab and the same Bash 4.3 / Apache CGI environment:

- [Shocker](../../challenges/startpoint/shocker/Shocker.md): integrated User and Root path.
- [CGI Environment](../../challenges/command-injection/shocker/cgi-shellshock.md): focused Shellshock foothold objective.
- [Perl Maintenance](../../challenges/linux-privilege-escalation/shocker/sudo-perl.md): focused sudo/Perl privilege objective.

The focused Challenges intentionally reuse the same User or Root Flag as the corresponding stage of the integrated Challenge; they do not require separate target images.

## Automated acceptance

The dedicated workflow .github/workflows/shocker-e2e.yml generates or reuses a versioned User/Root Manifest, verifies all three Challenge answer mappings, builds the target and a separate non-root HTTP attacker, then runs the complete Shellshock -> User Flag -> sudo Perl -> Root Flag path against one clean instance on an internal-only Docker network. The target receives no Flag environment variables. On main, verified release artifacts are committed automatically; PR runs use a temporary CI version and do not commit.

The Lab E2E is separate from Worker lifecycle, platform scheduling and backend grading.
