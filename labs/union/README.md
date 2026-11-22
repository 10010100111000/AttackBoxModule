# Union — November 2021 UHC Qualifiers

A reconstructed Linux Docker training target based on the retired Hack The Box Union by IppSec. This is not an official HTB image. The original private application repository is not publicly available, so the frontend and PHP routes are independently reconstructed from public evidence; the SQL database, filesystem reads, firewall commands, SSH and sudo behaviors use actual system components.

## Intended discovery path

1. Scan the network. HTTP 80 is accessible; SSH 22 is initially blocked by a real INPUT policy. The site presents the UHC November Qualifiers eligibility form and a Check button.
2. Players are checked against an actual MariaDB database named november. The original-style weak filter makes manual UNION SQL injection necessary. The one-column tables are players(player) and flag(one).
3. Extract the random UHC qualifier token from the real table and submit it on challenge.php. This authorizes the PHP session and redirects to firewall.php.
4. firewall.php runs the original-style sudo iptables command to grant the requester's source IP SSH access inside the container network namespace.
5. The SQL user has FILE privilege and MariaDB can read web files using LOAD_FILE. The app's config.php source leaks a deliberately reused password for the uhc SSH account.
6. Obtain the user flag at /home/uhc/user.txt, inspect firewall.php, and discover that it passes the untrusted X-Forwarded-For header to a shell command. The vulnerable web process runs as www-data and is configured for passwordless sudo. The root flag is /root/root.txt.

No arbitrary code is executed through a mock PHP endpoint, fake SQL parser, fake iptables binary, or simulated privilege-elevation result.

## Implementation and differences

- Retired original: Ubuntu 20.04, nginx 1.18, PHP, MySQL, OpenSSH and iptables.
- Reproduction: Alpine 3.20, PHP 8.3 + php-fpm, real MariaDB, nginx, OpenSSH, sudo and iptables, plus Bootstrap 4.1.1.
- UI follows the dark Bootstrap 4 eligibility and challenge forms shown in public screenshots. The original PHP site source was not released; this code recreates the observed routes and responses, not the original site's unpublished bytes.
- The server uses real SQL string interpolation, MariaDB INFORMATION_SCHEMA, native LOAD_FILE with FILE permission, PHP sessions, and a native iptables INPUT policy.
- A new qualifier token is generated during every container boot. Private foothold/root answers are separately injected by the Worker environment.
- All network/firewall rules apply inside the container's own namespace. SSH is not allowed from other network peers until the session flow adds the relevant iptables rule.

Original evidence:
- https://www.hackthebox.com/machines/union
- https://0xdf.gitlab.io/2021/11/22/htb-union.html
- https://pencer.io/ctf/ctf-htb-union/
- https://www.youtube.com/watch?v=z5pdizHDvt8

Bootstrap 4.1.1 is fetched from jsDelivr during the Docker build (MIT licensed).

## Isolated deployment

Build from the repository root:

    docker build -f labs/union/Dockerfile -t ttp-union:dev labs/union

Create a private network and start one instance (illustrative placeholders, not production flags):

    docker network create --internal union-lab
    docker run -d --name union-target --network union-lab \
      --cap-add NET_ADMIN --memory 384m --pids-limit 256 \
      -e UNION_REQUIRE_PRIVATE_FLAGS=1 \
      -e UNION_STATIC_USER_FLAG='TTP{private_user_from_worker}' \
      -e UNION_STATIC_ROOT_FLAG='TTP{private_root_from_worker}' \
      ttp-union:dev
    docker inspect -f '{{.State.Health.Status}}' union-target

Do not publish ports to a public host, do not use --privileged, do not use host networking, and never attach host filesystem mounts. The worker must provide a dedicated internal network namespace and NET_ADMIN capability for this specific target; if NET_ADMIN is unavailable, startup intentionally fails instead of emulating the firewall. Sudo requires that the instance NOT use no-new-privileges. These constraints must be reviewed before deployment into the main platform.

The public demo flags in the image must never be used as production answers. The real Worker must inject new private values on every instance start. The random UHC qualifier defaults to a fresh value; an explicit UNION_QUALIFIER_FLAG is accepted for deterministic fixture tests.

## CI and release gate

The current GitHub Actions workflow in .github/workflows/union.yml verifies actual image construction, PHP/MariaDB service startup, regular eligibility/flag routes, SSH gating, static private-flag injection, separate-instance isolation, and qualifier rotation after re-creation.

This initial smoke workflow does not yet prove the full exploitation chain. Independent remote verification of UNION-based file reads, SSH password reuse, HTTP header injection, and sudo root privileges is REQUIRED before moving the PR out of Draft. Also check real image size, memory, runtime capability compatibility, and Worker network enforcement. Do not claim Union production-ready based on a green startup-only CI check.
