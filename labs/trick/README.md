# Trick — DNS / SQLi FILE / nested traversal / Fail2ban

**Status: implementation under independent Docker acceptance.** This is an independent training reconstruction of the retired HTB Trick machine, not the original VM or original private application source. It preserves the observable attack sequence and uses real services and real OS permissions; it does not claim byte-for-byte source fidelity.

## Learning objectives

- file_read.nested-traversal: bypass a one-pass ../ removal with a nested traversal path.
- file_read.lfi: make a real PHP include() read files outside the intended web directory.
- sqli.auth-bypass: exploit an unsafe SQL query in the payroll login workflow.
- sqli.file-operations: use MariaDB's real FILE privilege and LOAD_FILE() to infer the contents of an OS-readable Nginx configuration file.
- Linux identity boundaries: distinguish the MariaDB service account from the Marketing PHP-FPM worker running as michael.
- Fail2ban action execution: modify a real Fail2ban action file through a group-writable directory, restart the real service through the narrow sudo rule, and cause the root-run action to disclose the Root Flag.

## Observable attack path

1. Query the target's reverse DNS record and request an AXFR transfer for trick.htb.
2. Discover the payroll virtual host from the transferred zone.
3. Inspect the normal payroll login request and identify the unsafe SQL query.
4. Use boolean conditions against LOAD_FILE('/etc/nginx/http.d/trick.conf') to discover the separate Marketing virtual host. The test proves both true and false responses and also proves MariaDB cannot read michael's mode-0600 SSH private key.
5. Browse the Marketing site and inspect its page parameter. The PHP application removes ../ once, so a nested ....// path reaches real files.
6. Read the actual michael SSH private key through PHP-FPM, then authenticate to the target's real OpenSSH server.
7. Inspect the security group, the Fail2ban action directory and the exact sudo command.
8. Replace the active iptables-multiport wrapper's inherited actionban command, restart Fail2ban, trigger the SSH jail and read the Root Flag after the temporary ban expires.

The root-stage behavior follows the public Trick writeup's Fail2ban action misconfiguration. The action copies the protected Root Flag to a temporary path while running as root; this reconstruction proves the Root Flag read rather than claiming that the player receives a persistent root shell.

## Real components and deliberate reconstruction choices

| Component | Implementation |
|---|---|
| DNS | ISC BIND authoritative zone, AXFR enabled, per-instance PTR record |
| Web | Nginx with separate default, Payroll and Marketing virtual hosts |
| Payroll | PHP 8.4 application with a real MariaDB query and an intentionally unsafe username interpolation |
| Database | MariaDB; the remo account has SELECT on the application schema and the genuine global FILE privilege |
| Marketing | PHP-FPM pool runs as the real michael Unix account |
| SSH | OpenSSH; a real per-instance keypair is generated for michael |
| Privilege boundary | Fail2ban 1.1, an OpenSSH-session-aware Fail2ban filter, iptables, a real group-writable action directory and a real sudo service restart |

The original machine used an older Linux/web stack. This reconstruction uses a small supported Alpine 3.22 base and current packaged services while preserving the vulnerable behaviors and the OS identity/permission boundaries. The SMTP/mail-spool alternate route is intentionally omitted; the main DNS → SQLi/FILE → PHP include → SSH → Fail2ban path is retained.

There are no mock SQL parsers, fake file-read endpoints, simulated shell outputs or fake privilege-escalation helpers. SQL injection reaches MariaDB; LOAD_FILE() reads files as the MariaDB OS user; PHP include() executes in a real PHP-FPM worker; SSH uses a real private key; Fail2ban runs its actual action as root.

## Build and isolated run

    docker build -f labs/trick/Dockerfile -t ttp-trick:dev labs/trick

    docker network create --internal trick-lab
    docker run -d --name trick-target --network trick-lab \
      --network-alias trick.htb --network-alias preprod-payroll.trick.htb \
      --cap-drop NET_ADMIN --memory 512m --cpus 2 --pids-limit 256 \
      -e TRICK_STATIC_USER_FLAG='TTP{private_user_flag}' \
      -e TRICK_STATIC_ROOT_FLAG='TTP{private_root_flag}' \
      ttp-trick:dev

    docker inspect -f '{{.State.Health.Status}}' trick-target

Do not publish the container ports to the public Internet. The platform's private target network must expose TCP 80/22 and TCP+UDP 53 to the player's AttackBox. No host network, privileged mode, host mount or Docker socket is used.

## Flag and reset contract

The Worker passes TRICK_STATIC_USER_FLAG and TRICK_STATIC_ROOT_FLAG as opaque per-instance values. The target writes them to:

- /home/michael/user.txt — michael can read the User Flag.
- /root/root.txt — root-only, mode 0600.

The Web backend validates submitted values. Worker only schedules and starts/stops the target; it does not inspect the exploit or judge Flags.

No persistent data volume is declared. A new container generates a new MariaDB database, database credential, SSH account password, SSH keypair and host keys. Destroy/recreate resets the challenge state and receives a new Flag pair.

## Resource and security requirements

- Multi-stage Docker build; PHP sources are linted in the build stage.
- Runtime base is Alpine 3.22; no Ubuntu base image.
- Healthcheck covers MariaDB, all three HTTP virtual hosts, BIND AXFR/PTR, PHP-FPM, SSH and the Fail2ban jail.
- Independent acceptance measures image bytes, memory and PIDs.
- The target needs NET_ADMIN for Fail2ban's iptables action. This capability must be granted only to this target and only inside its private network namespace. It must not be generalized to other labs or combined with host networking/privileged mode.
- Production release remains blocked until the actual Worker can apply this per-target capability and isolation policy, and the platform's static answer mapping is checked.

## Independent acceptance

.github/workflows/trick.yml uses a separate attacker container and must prove:

1. PTR and AXFR discovery.
2. Distinct default, Payroll and Marketing vhosts.
3. True/false SQLi behavior and actual MariaDB LOAD_FILE() access to the Nginx config.
4. MariaDB cannot read michael's mode-0600 SSH key.
5. Nested traversal reads /etc/passwd, confirms the PHP-FPM UID and retrieves the actual SSH private key.
6. SSH as michael, User Flag access, group membership, writable action directory and the exact sudo rule.
7. The real Fail2ban action executes as root and exposes the Root Flag.
8. A fresh instance starts with different Flags and no prior /tmp/root.txt state.

A passing lab CI does not prove actual Worker deployment or release readiness.
