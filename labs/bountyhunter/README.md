# BountyHunter — PHP XXE, SSH credential reuse and Skytrain eval

Independent reconstruction of the retired 2021 HTB BountyHunter. The original source and static assets were not released; routes, layout and behavior are reconstructed from public observations and writeups.

## Real components and trust boundaries

- Apache and PHP 8.3 FPM expose the Bounty Hunters portal and beta report form.
- The browser JavaScript serializes report fields as base64 XML and submits them to tracker_diRbPr00f314.php.
- The tracker uses genuine PHP SimpleXML/libxml with entity substitution enabled. PHP stream wrappers are available to external entities.
- The exposed db.php configuration contains the beta credential reused by the development SSH account.
- Native OpenSSH provides the development account. Its sudoers rule permits only the Skytrain ticketValidator.py script.
- The ticket validator uses Python eval on a ticket expression after a weak numeric check; sudo runs it as root.

## Challenge reuse

These three Challenges share this one Lab image and runtime:

- [BountyHunter](../../challenges/startpoint/bountyhunter/BountyHunter.md): integrated XML foothold and Skytrain root path.
- [XML External Entity](../../challenges/file-security/bountyhunter/xml-external-entity.md): focused PHP XXE and development foothold.
- [Skytrain Ticket Validation](../../challenges/linux-privilege-escalation/bountyhunter/skytrain-eval.md): focused sudo/Python eval privilege escalation.

The focused Challenges reuse the corresponding User or Root Flag from the integrated Challenge. They do not create separate Docker images or duplicate the PHP portal, SSH service or Skytrain validator.

## Fidelity and limitations

- The original private source was unavailable. The public portal flow and vulnerable parser behavior are reconstructed from public writeups.
- The beta database integration remains unfinished, consistent with the original public observations; no pretend database backend is added.
- Skytrain uses the actual Python eval behavior. The runtime Python version is Alpine's Python 3, not the original Ubuntu Python 3.8.
- The container uses Alpine 3.20, Apache, PHP 8.3 FPM, OpenSSH, sudo and Python.
- Do not expose the vulnerable HTTP/SSH services to the public Internet. Run each instance on a dedicated isolated internal bridge.

## Build

~~~sh
docker build -f labs/bountyhunter/Dockerfile -t ttp-bountyhunter:dev labs/bountyhunter
docker network create --internal bountyhunter-dev
docker run -d --name bountyhunter-target --network bountyhunter-dev \
  --memory 192m --pids-limit 128 \
  -e BOUNTYHUNTER_REQUIRE_PRIVATE_FLAGS=1 \
  -e BOUNTYHUNTER_STATIC_USER_FLAG='TTP{private_user}' \
  -e BOUNTYHUNTER_STATIC_ROOT_FLAG='TTP{private_root}' \
  ttp-bountyhunter:dev
docker inspect -f '{{.State.Health.Status}}' bountyhunter-target
~~~

## Flags

Development seeds are stored in flags/user.txt and flags/root.txt. Each isolated instance should receive BOUNTYHUNTER_STATIC_USER_FLAG, BOUNTYHUNTER_STATIC_ROOT_FLAG and BOUNTYHUNTER_REQUIRE_PRIVATE_FLAGS=1. The entrypoint writes the values with the intended ownership and permissions, then unsets the variables before starting services.

## Automated acceptance

The dedicated .github/workflows/bountyhunter-e2e.yml builds the target and a separate non-root attacker, generates one random User/Root Flag pair, and runs the complete HTTP XXE -> credential recovery -> SSH -> sudo Skytrain eval path against one clean instance on an internal-only Docker network. The attacker compares the exact values recovered through the real path. No second target instance is started.

The Lab E2E is separate from Worker lifecycle, platform scheduling and backend grading.
