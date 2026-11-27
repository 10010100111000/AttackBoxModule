# Nibbles — authentic Nibbleblog 4.0.3

An independent Linux Docker reconstruction based on the retired Hack The Box Nibbles machine. It is not an official HTB image, and the unpublished original home page and `personal.zip` contents are not claimed to have been recovered.

## Real vulnerable components

- Upstream Nibbleblog 4.0.3, pinned to commit `6fe138276e82ed604bb35a960327a4ac0b485097`.
- Original PHP CMS login, XML-backed users/configuration and My Image plugin.
- The original plugin configuration controller uses `move_uploaded_file()` without restricting executable extensions (CVE-2015-6967).
- Apache/PHP runs as the unprivileged `nibbler` account.
- Native sudoers rule permits the user to execute a fixed monitoring script as root; the script itself is user-writable.

The original Nibbleblog source, license and copyright files are retained. The container uses Alpine 3.15 and PHP 7.4 rather than the original Ubuntu 16.04 environment; this OS/PHP difference is intentional and not hidden behind a forged version fingerprint.

Public references:
- [Upstream Nibbleblog commit](https://github.com/dignajar/nibbleblog/commit/6fe138276e82ed604bb35a960327a4ac0b485097)
- [CVE-2015-6967 advisory](https://github.com/advisories/GHSA-jc49-pxch-59wj)
- [Original machine writeup](https://cornfield.sh/htb-nibbles/)

## Discovery path

1. Inspect the simple home page and its HTML source to discover the CMS directory.
2. Identify the real CMS version from its public README/configuration and inspect the native login.
3. Enter the CMS and investigate the My Image plugin.
4. Exploit the original upload handler to execute PHP as `nibbler`.
5. Inspect the user's archive and the sudo rule for the monitoring script.
6. Modify the user-writable script, run it through the permitted sudo command and obtain root.

## Build and local isolated use

From the repository root:

~~~sh
docker build -f labs/nibbles/Dockerfile -t ttp-nibbles:dev labs/nibbles
docker network create --internal nibbles-lab
docker run -d --name nibbles-target --network nibbles-lab \
  --memory 160m --pids-limit 128 \
  -e NIBBLES_REQUIRE_PRIVATE_FLAGS=1 \
  -e NIBBLES_STATIC_USER_FLAG='TTP{instance_user_answer}' \
  -e NIBBLES_STATIC_ROOT_FLAG='TTP{instance_root_answer}' \
  ttp-nibbles:dev
docker inspect -f '{{.State.Health.Status}}' nibbles-target
~~~

Do not publish the vulnerable services to the public Internet. The target requires no privileged mode, host networking, Docker socket or host filesystem mount.

## Automated acceptance

`.github/workflows/nibbles-e2e.yml` builds the target and a separate non-root HTTP attacker. The attacker uses the real CMS login and plugin upload route, then continues through the PHP execution context to verify the actual nibbler identity, User Flag, sudo permission, UID 0 and Root Flag.

The workflow uses one clean instance with distinct random User and Root Flags, runs the complete chain once, then recreates that same Lab and checks that the uploaded PHP file is gone. The target and attacker share only an internal Docker network.

## Resource profile

The previous image-only CI measured approximately 25 MiB and 17.2 MiB runtime memory with 8 PIDs. The new full-chain workflow records its own image size and per-instance memory after the attack; use those measurements as the current baseline.
