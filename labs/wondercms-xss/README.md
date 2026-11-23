# WonderCMS 3.4.2 — reflected XSS with an in-container administrator review bot

**Status: real player-to-Flag path implemented; awaiting final CI and actual Worker-network smoke.** This is an independent training reconstruction, not an official HTB/OffSec image.

## Training objective

- Primary topic: **reflected XSS in an HTML form-action attribute** — CVE-2023-41425.
- Intended level: **intermediate**. Players discover a normal publishing site, identify the contact form and WonderCMS, submit a crafted website URL, and use an administrator-browser XSS to obtain a private Flag.
- The vulnerable upstream index.php is unmodified WonderCMS 3.4.2 pinned to commit 65ad81405af2d27f75190805ed6c1d954d6fc72b.
- The public contact form is a separate challenge application component. It stores website submissions in an instance-local queue; it does not itself implement an XSS handler.

## Correct runtime architecture

The Worker starts **one target image/container**. This image runs two unprivileged service processes:

1. **PHP / WonderCMS** (www-data): public site, real contact form, original vulnerable CMS, and /review-proof.php. The Flag endpoint is protected by the native WonderCMS administrator PHP session.
2. **Admin Review Bot** (wcmsbot): a separate Python process with a real headless Chromium/ChromeDriver. It polls the contact queue, logs into WonderCMS with the instance's private admin account, and visits each submitted website URL in the admin browser.

The bot extracts only the submitted URL's path/query and visits it on the local WonderCMS origin; it never navigates to the submitted hostname. The injected script can read the admin-only Flag using the admin session and exfiltrate it to the player's listener on the same private per-user lab network. The player then submits that Flag to trytopwn.

**No Worker code changes or Worker-side browser/Flag logic are needed.** Worker only starts/stops the target image, supplies resource limits, and provides the per-user isolated lab network. The Web backend checks the player's submitted answer.

### Process isolation inside the target

- PHP runs as www-data; the bot runs as a separate wcmsbot user.
- The Flag file is readable only by the PHP service account; the bot does not open or read it from disk. It obtains the Flag only through the authenticated browser session and the vulnerable XSS path.
- Chromium runs as non-root with its sandbox enabled (no --no-sandbox), a temporary per-review profile, no host mounts and no Docker socket.
- The bot accepts only absolute HTTP(S) URLs but discards the submitted authority, visiting only the local app path. The intended exfiltration destination is the learner's private AttackBox address on that instance's isolated lab network.
- Contact submissions are queued atomically with a bounded pending queue; each browser review has a page-load timeout and a short visit window.
- Container reset clears the admin session, bot profile, queue and instance Flag.

## Sources and fidelity

- Upstream WonderCMS release: https://github.com/WonderCMS/wondercms/releases/tag/3.4.2
- CVE advisory: https://github.com/advisories/GHSA-58rr-37rr-r6h5
- Original disclosure: https://gist.github.com/prodigiousMind/fc69a79629c4ba9ee88a7ad526043413
- HTB Sea's public writeup documents the same real pattern: public contact form stores a submitted website, an admin headless browser visits it, and the reflected WonderCMS XSS executes in that browser: https://0xdf.gitlab.io/2024/12/21/htb-sea.html
- WonderCMS upstream MIT license is retained in the image at /srv/wcms/LICENSE-WonderCMS.

## Build and isolated local test

    docker build -t ttp-wondercms-xss:dev -f labs/wondercms-xss/Dockerfile labs/wondercms-xss
    docker network create --internal wcms-lab
    docker run -d --name wcms-target --network wcms-lab --memory 512m --cpus 1 --pids-limit 256 \
      -e WONDERCMS_REQUIRE_PRIVATE_FLAGS=1 \
      -e WONDERCMS_ADMIN_PASSWORD='use-a-private-test-password' \
      -e WONDERCMS_STATIC_XSS_FLAG='TTP{local_test_value}' \
      ttp-wondercms-xss:dev

Connect the AttackBox to the same private per-user lab network and submit a URL through /contact.php. Do not publish the target's vulnerable HTTP port to the public Internet.

## Acceptance criteria

The independent attacker container must:
1. Browse the public site and contact form without knowing the admin password.
2. Confirm direct anonymous requests to /review-proof.php are forbidden and /data/database.js is not public.
3. Submit a URL containing the original WonderCMS reflected-XSS vector through the normal contact form.
4. Receive the private per-instance Flag at its own listener after the target-local admin bot visits the URL. The attacker container must never receive the admin password or read target files.
5. Repeat after destroying/recreating the target with a different admin password and Flag.

The browser is part of the **target image**, not the CI-only tester. Chromium increases the runtime image and memory requirement; the CI reports the measured image size and memory snapshot rather than assuming it is small.

## Release boundary

The source-level target-to-bot-to-Flag path must pass the full black-box CI. Before removing .release-blocked, also verify the existing Worker can start this single image with the configured memory limit and that the bot's callback reaches only the same user's AttackBox over the existing private lab network. This is a Worker deployment/network smoke test, **not a request for Worker to implement a bot or Flag judge**.
