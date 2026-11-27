# BountyHunter — PHP/libxml XXE and Skytrain ticket validation

This is an independent reconstruction of the retired HTB BountyHunter machine. The original website source and static assets were not published; the page layout and report workflow are reconstructed from public observations. The vulnerable components and attack behavior are real.

## Real components and boundaries

- Apache with PHP 8.3 FPM and native SimpleXML/libxml.
- The beta report tracker accepts base64-encoded XML and parses it with entity substitution enabled.
- XXE can read local files through the actual PHP/libxml parser. The PHP configuration file contains the credential reused by the development SSH account.
- Native OpenSSH provides the development account.
- Native sudoers permits development to run one specific Python ticket validator as root.
- The real Skytrain validator evaluates ticket content using Python eval() in the sudo process.

## Challenge reuse

Three learner Challenges reuse this one Lab image and the same PHP/SSH/Skytrain environment:

- [BountyHunter](../../challenges/startpoint/bountyhunter/Bountyhunter.md): integrated XXE → SSH → sudo eval path.
- [Report Parser](../../challenges/file-security/bountyhunter/xxe-file-read.md): focused XXE file-read and credential recovery.
- [Skytrain Validator](../../challenges/linux-privilege-escalation/bountyhunter/skytrain-eval.md): focused Python eval privilege escalation.

The focused Challenges reuse the corresponding User or Root Flag from the integrated Challenge. They do not create separate images or duplicate the application.

## Build

~~~sh
docker build -f labs/bountyhunter/Dockerfile -t ttp-bountyhunter:dev labs/bountyhunter
docker network create --internal bountyhunter-dev
docker run -d --name bountyhunter-target --network bountyhunter-dev \
  --memory 192m --pids-limit 128 \
  -e BOUNTYHUNTER_REQUIRE_PRIVATE_FLAGS=1 \
  -e BOUNTYHUNTER_STATIC_USER_FLAG='TTP{instance_user}' \
  -e BOUNTYHUNTER_STATIC_ROOT_FLAG='TTP{instance_root}' \
  ttp-bountyhunter:dev
docker inspect -f '{{.State.Health.Status}}' bountyhunter-target
~~~

Do not expose the vulnerable target to the public Internet. It does not require privileged mode, host networking, Docker socket access or host filesystem mounts.

## Flags

The files in flags/ are development seeds only. Isolated instances must provide BOUNTYHUNTER_STATIC_USER_FLAG, BOUNTYHUNTER_STATIC_ROOT_FLAG and BOUNTYHUNTER_REQUIRE_PRIVATE_FLAGS=1. The entrypoint writes the values with deliberate ownership and permissions and removes the variables before starting services.

## Automated acceptance

The dedicated .github/workflows/bountyhunter-e2e.yml builds one target image and a separate non-root attacker. The attacker follows the real report form, uses the native XML parser to read the PHP config and recover the development SSH credential, logs in to retrieve the exact User Flag, then uses the real sudo-authorized Skytrain validator to execute as root and retrieve the exact Root Flag.

CI generates one random User/Root Flag pair for a single clean target instance, masks the values and compares them byte-for-byte. It does not use docker exec for exploitation or start a second target instance. Worker lifecycle and production grading remain separate.
