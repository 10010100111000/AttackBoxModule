# Bashed — genuine Arrexel/phpbash and root cron

Retired HTB Linux machine reconstruction using the original Arrexel/phpbash project under Apache/PHP. Not an official HTB image; the HTB landing page source was not published, so the public homepage is a small independent reconstruction.

## Real components and trust boundaries

- Original Arrexel/phpbash single-file web shell, pinned by Git object hash dd7ff714ad62ddcf2a06a7a44af9c342b7d83552; Apache License 2.0 retained.
- Apache/PHP invokes the original shell_exec() implementation as www-data.
- Native sudoers permits www-data to switch to scriptmanager without a password.
- A real root cron entry executes every Python file in /scripts once per minute.
- /scripts/test.py is owned and writable by scriptmanager; the cron process runs it as root.

## Challenge reuse

The following learner Challenges share this one Lab image and the same runtime environment:

- [Bashed](../../challenges/startpoint/bashed/Bashed.md): integrated Web foothold and root cron path.
- [Developer Console](../../challenges/code-execution/bashed/phpbash-webshell.md): focused phpbash discovery and www-data execution.
- [Scheduled Maintenance](../../challenges/linux-privilege-escalation/bashed/root-cron.md): focused scriptmanager/root cron privilege boundary.

The focused Challenges intentionally reuse the corresponding User or Root Flag from the integrated Challenge. They do not create separate Docker images or duplicate the vulnerable application.

## Build

~~~sh
docker build -f labs/bashed/Dockerfile -t ttp-bashed:dev labs/bashed
docker run -d --name bashed --network none --memory 256m --pids-limit 192 ttp-bashed:dev
docker inspect -f '{{.State.Health.Status}}' bashed
~~~

## Flags

Default files are development seeds only: /home/arrexel/user.txt and /root/root.txt. For isolated instances, inject BASHED_STATIC_USER_FLAG, BASHED_STATIC_ROOT_FLAG and BASHED_REQUIRE_PRIVATE_FLAGS=1. The entrypoint writes them with deliberate ownership and permissions and removes the variables before starting Apache and cron.

## Automated acceptance

The dedicated workflow .github/workflows/bashed-e2e.yml builds one target image and a separate non-root attacker. The attacker discovers the original phpbash interface over HTTP, proves execution as www-data, pivots to scriptmanager, modifies the actual /scripts/test.py and waits for the real root cron job to run it. The test retrieves and byte-compares the exact random User and Root Flags generated for that single CI instance. It does not execute the script directly as root or start a second target instance.

The Lab E2E is separate from Worker lifecycle, platform scheduling and backend grading.
