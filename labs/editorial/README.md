# Editorial — SSRF and GitPython privilege escalation

An independent reconstruction based on the retired Hack The Box Editorial machine. It is not an official HTB image, and its unpublished HTML/Python source is not claimed to have been recovered.

## Learning path

The player begins with the public publishing website and its book-cover preview. The preview performs a genuine server-side HTTP request and stores the returned bytes. Discover the loopback-only Flask metadata API, use the exposed onboarding information to access the real SSH service as `dev`, inspect the developer's two-commit Git history, recover the removed production credential, then audit the restricted sudo rule and vulnerable GitPython 3.1.29 deployment helper.

## Real components

- Flask publishing site behind Nginx, with Home, About and Publish with us pages.
- Real server-side HTTP fetch in the book cover preview; no synthetic SSRF endpoint.
- Separate Flask metadata API bound to `127.0.0.1:5000`, not directly reachable from the attacker container.
- Native OpenSSH with `dev` and `prod` accounts.
- Two real Git commits at `/home/dev/apps`; the older commit contains the removed production credential.
- GitPython 3.1.29, native Git and a narrowly scoped sudo rule for the production clone helper. GitPython 3.1.29 is affected by CVE-2022-24439.
- Per-instance User and Root Flags injected at startup.

This is a source-based reconstruction from public machine behavior and writeups. It does not claim to recover HTB's private original application source.

## Build

~~~sh
docker build -f labs/editorial/Dockerfile -t ttp-editorial:dev labs/editorial
~~~

For local isolated use, create an internal Docker network and provide both instance Flags:

~~~sh
docker network create --internal editorial-lab
docker run -d --name editorial-target --network editorial-lab \
  --memory 512m --pids-limit 192 \
  -e EDITORIAL_REQUIRE_PRIVATE_FLAGS=1 \
  -e EDITORIAL_STATIC_USER_FLAG='TTP{instance_user_answer}' \
  -e EDITORIAL_STATIC_ROOT_FLAG='TTP{instance_root_answer}' \
  ttp-editorial:dev
~~~

Do not publish the target ports to the public Internet. No privileged mode, host networking, Docker socket or host filesystem mount is required.

## Automated acceptance

`.github/workflows/editorial-e2e.yml` builds the target and a separate attacker image. The independent attacker runs on an internal-only Docker network and verifies the full path from the public cover-preview workflow through the private metadata API, real SSH accounts and historical Git credential to the vulnerable GitPython deployment helper. It checks the exact User and Root Flag values supplied to each instance and repeats the test on two clean instances with different values.

## Release boundary

The Lab's Docker build, startup, health and independent attack-chain E2E are separate from platform Worker lifecycle, per-user network scheduling and production grading. The `.release-blocked` marker remains for those platform release gates; passing Lab E2E does not remove it.
