# Editorial — Web SSRF and GitPython historical vulnerability lab

An independent reconstruction based on the retired Hack The Box Editorial machine. It is not an official HTB image, and its unpublished HTML/Python source is not claimed to have been recovered.

## What has been implemented

- An ordinary publishing website called Editorial Tiempo Arriba with Home, About and Publish with us.
- The book cover preview makes a genuine server-side HTTP request and stores the returned bytes at an unguessable path under /static/uploads. It does not use a synthetic vulnerability endpoint.
- A separate Flask metadata API bound to 127.0.0.1:5000, unavailable to external containers directly; the normal publishing website listens behind Nginx on port 80.
- An actual OpenSSH service with dev and prod accounts; the private API contains a deliberately exposed onboarding credential.
- A genuine two-commit Git history at /home/dev/apps in which a production credential was removed from the latest file but remains available in the older commit.
- The actual GitPython 3.1.29 package, native git executable, a deployment cloning helper calling Repo.clone_from, and a restricted sudoers rule for the prod account. GitPython 3.1.29 is affected by CVE-2022-24439 according to the upstream security advisory.
- Demo User and Root Flags, plus independent per-instance startup injection using EDITORIAL_STATIC_USER_FLAG and EDITORIAL_STATIC_ROOT_FLAG.

Public references:
- Official machine: https://www.hackthebox.com/machines/Editorial
- Contemporary writeup: https://www.brunorochamoura.com/posts/editorial/
- Vulnerable dependency advisory: https://github.com/advisories/GHSA-hcpj-qp55-gfph

The public frontend is a newly authored recreation of the observed publishing-house design. No proprietary original website source or image assets are claimed.

## Intended discovery sequence

First discover the book submission flow, then determine that book cover preview fetches the provided address from the target server. Investigate which internal services can be reached, use the information revealed by the internal API to understand account access, then inspect the history of the developer's local Git repository. Finally, review the permissions and vulnerable dependencies in the production deployment workflow.

## Build and isolated use

From the repo root:

    docker build -f labs/editorial/Dockerfile -t ttp-editorial:dev labs/editorial

On an isolated Docker host:

    docker network create --internal editorial-lab
    docker run -d --name editorial-target --network editorial-lab \
      --memory 256m --pids-limit 128 \
      -e EDITORIAL_REQUIRE_PRIVATE_FLAGS=1 \
      -e EDITORIAL_STATIC_USER_FLAG='TTP{instance_user_answer}' \
      -e EDITORIAL_STATIC_ROOT_FLAG='TTP{instance_root_answer}' \
      ttp-editorial:dev

No public host port publication, --privileged, host networking, Docker socket mount or host filesystem mount is permitted.

## CI scope and release gate

The current CI builds the original components, creates an isolated attacker container, verifies port isolation, genuine SSRF and internal API discovery, verifies service health, checks the pinned GitPython dependency and sudo configuration, and checks flag rotation after a fresh instance.

**Full interactive SSH pivot and native GitPython-to-root exploitation have not yet passed an independent automated end-to-end acceptance test. This box is a development candidate, not a verified web-to-root machine. Do not merge or release on the basis of green smoke CI alone.**

Measured image footprint is reported in GitHub Actions. Resource limits are test boundaries, not a measured capacity guarantee.
