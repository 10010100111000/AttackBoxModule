# Trick — DNS / SQLi FILE / nested traversal / Fail2ban

**Status:** existing multi-service reconstruction; independent E2E acceptance is being added. This is an independent training reconstruction of the retired HTB Trick machine, not the original VM or private application source. It preserves the observable attack sequence and uses real services and OS permissions.

## Learning objectives

- DNS reconnaissance: reverse lookup and AXFR.
- SQL injection: unsafe MariaDB query and conditional inference.
- Database FILE privilege: use the real MariaDB LOAD_FILE() boundary to read a configuration file accessible to the mysql service account.
- Nested traversal and LFI: bypass one-pass ../ removal and execute a real PHP include as the Marketing service account.
- SSH: use a real per-instance private key to authenticate as michael.
- Linux permissions and Fail2ban: modify a real group-writable action directory and trigger a root-run action through the narrow sudo rule.

## Attack path

1. Reverse DNS and AXFR reveal the Payroll virtual host.
2. Payroll login SQLi plus MariaDB LOAD_FILE() distinguishes true/false conditions and reveals the Marketing virtual host from the actual Nginx configuration.
3. Marketing PHP include uses a one-pass ../ removal; nested ....// traversal reads real files.
4. The Marketing PHP-FPM worker runs as michael, allowing it to read michael's real SSH private key.
5. SSH as michael exposes the User Flag and the group-writable Fail2ban action directory.
6. A narrow sudo rule permits only the Fail2ban service restart. A modified real actionban executes as root and discloses the Root Flag.

The SMTP/mail-spool alternate route from the original machine is omitted. The retained path is DNS → SQLi/FILE → PHP include → SSH → Fail2ban.

## Real components

| Component | Implementation |
|---|---|
| DNS | ISC BIND authoritative zone, AXFR and per-instance PTR |
| Web | Nginx, separate default/Payroll/Marketing virtual hosts |
| Payroll | PHP 8.4 and real MariaDB query |
| Marketing | PHP-FPM pool running as michael |
| SSH | OpenSSH with a per-instance keypair |
| Privilege boundary | Fail2ban, iptables, group-writable action directory and narrow sudo service restart |

The target needs NET_ADMIN only inside its own private network namespace so Fail2ban can run its actual iptables action. No host network, privileged mode, host mount or Docker socket is used.

## Build and local run

    docker build -f labs/trick/Dockerfile -t ttp-trick:dev labs/trick
    docker network create --internal trick-lab
    docker run -d --name trick-target --network trick-lab \
      --network-alias trick-target --cap-add NET_ADMIN \
      --memory 512m --cpus 2 --pids-limit 256 \
      -e TRICK_STATIC_USER_FLAG='TTP{private_user_flag}' \
      -e TRICK_STATIC_ROOT_FLAG='TTP{private_root_flag}' \
      ttp-trick:dev

Do not publish this intentionally vulnerable service to the public Internet.

## Flag lifecycle

The target accepts two opaque per-instance values through TRICK_STATIC_USER_FLAG and TRICK_STATIC_ROOT_FLAG and writes them to:

- /home/michael/user.txt — User Flag, readable by michael
- /root/root.txt — Root Flag, mode 0600

scripts/generate_trick_release.py --version 0.1.0 creates a random versioned pair and synchronizes the manifest and the two Challenge answers. Re-running the same version reuses the same pair; a new version generates a new pair. The E2E workflow generates a fresh pair for each CI run and passes it through the same target environment variables.

## Independent acceptance

- tests/acceptance.py: independent player across DNS, HTTP and SSH.
- tests/Dockerfile.attacker: small attacker image with dig, ssh and sshpass.
- .github/workflows/trick-e2e.yml: private-network full-chain E2E, exact User/Root Flag verification.
- .github/workflows/trick-release.yml: versioned release that runs the same full chain before committing the manifest and Challenge answers.

The attacker uses only exposed DNS, HTTP and SSH services. It never mounts the target filesystem, uses Docker socket or calls docker exec.

## Release boundary

The .release-blocked marker remains because actual Worker capability and platform answer mapping are outside this Lab task. It does not prevent isolated GitHub Actions E2E. No Worker or production deployment validation is claimed here.
