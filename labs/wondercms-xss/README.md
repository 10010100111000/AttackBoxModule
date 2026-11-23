# WonderCMS 3.4.2 — CVE-2023-41425

**Status: XSS browser proof verified, but the ordinary learner-to-Flag path is incomplete. Not an official OffSec/HTB image; NOT RELEASE-READY.**

A small, real PHP CMS built from the unmodified WonderCMS 3.4.2 upstream Git tag, checked against commit `65ad81405af2d27f75190805ed6c1d954d6fc72b`. WonderCMS uses a JSON file instead of MySQL. The deployment includes a real WonderCMS theme, administrator login and the original XSS-relevant page/form rendering code.

## Why this XSS target

- Primary topic: XSS, subtype: reflected XSS through HTML form attribute/context (CVE-2023-41425).
- Learner level: intermediate comprehensive browser exercise, rather than a beginner `alert(1)` echo page.
- Normal reconnaissance: discover the ordinary editorial website, identify WonderCMS, inspect admin login and navigation, and research the reported vulnerability.
- Actual vulnerability is in the upstream CMS source. **We do not modify its input handling or add a fake vulnerable endpoint.**
- The site text in its native `data/database.js` is seeded with ordinary publication content (not an invented exploit UI).

Sources:
- Upstream release: https://github.com/WonderCMS/wondercms/releases/tag/3.4.2
- CVE advisory: https://github.com/advisories/GHSA-58rr-37rr-r6h5
- Original disclosure: https://gist.github.com/prodigiousMind/fc69a79629c4ba9ee88a7ad526043413
- Upstream code license: MIT, retained within image at `/srv/wcms/LICENSE-WonderCMS`

## Architecture

- **Target image**: PHP 8.2 Alpine, the actual WonderCMS 3.4.2 frontend, native session support, local JSON storage; no Node, Java, Python, MySQL, Chromium or browser in the target.
- The built-in PHP router only implements equivalent routing and denies public access to the JSON database, as the original Apache `.htaccess` normally does. It does not add an exploitable route.
- **Objective**: `review-proof.php` returns one per-instance training Flag only when the CMS native administrator session is authenticated. It is not a vulnerable entrypoint and returns 403 to unauthenticated requests. The Flag is created at runtime in `/run/wcms/review.flag`.
- The actual XSS route is not linked as a `/vuln` page or listed in the visitor UI.
- **Current limitation**: The original XSS demonstration is in an *authenticated admin browser context*. CI logs in as the CMS administrator before running the benign proof. Ordinary learners do not have that session. For a real intermediate cross-user scenario, any visiting administrator/browser process is part of **this challenge's own environment**, NOT Worker. For a simpler directly returned Flag, select/implement an authentic public XSS variant that does not require someone else's session; do not make the admin-only Flag publicly accessible as a shortcut.

## Local isolated build and startup

    docker build -t ttp-wondercms-xss:dev -f labs/wondercms-xss/Dockerfile labs/wondercms-xss
    docker network create --internal wcms-lab
    docker run -d --name wcms-target --network wcms-lab --memory 128m --pids-limit 96 \
      -e WONDERCMS_REQUIRE_PRIVATE_FLAGS=1 \
      -e WONDERCMS_ADMIN_PASSWORD='use-a-private-test-password' \
      -e WONDERCMS_STATIC_XSS_FLAG='TTP{local_test_value}' \
      ttp-wondercms-xss:dev

No host ports should be published to the public Internet. The instance works through a private attack environment. Source-code inclusion is not a license to deploy a live vulnerable CMS on a public host.

## Verification gates

1. Build from exact source commit and test that PHP extensions (curl/zip/mbstring) and core site work.
2. Confirm visitors get 403 from the admin-only proof and cannot directly read `data/database.js`.
3. A separate actual Chromium browser signs in through the real WonderCMS login, opens a crafted page URL and proves JavaScript executed in the administrator origin. Checking a string in HTTP response is *not* acceptance.
4. In the admin browser proof, a private per-instance flag must be accessible only after real login, not returned to a visitor.
5. Recreate the target with a different private flag and password; previous sessions, submitted changes and proof must be gone.
6. CI reports image size and browser evidence. A complete learner-to-Flag path must be delivered by this challenge; the **Web backend** (not Worker) already validates submitted Flags. Worker is limited to target orchestration, networking and lifecycle.

**Do not claim the learner path is complete merely because a test account can log in as administrator. The Worker is NOT responsible for browser victims or Flag validation.**

## Verified results — 2026-11-23

- **PASS**: [independent real Chromium CI](https://github.com/10010100111000/AttackBoxModule/actions/runs/45203163868) against the genuine upstream 3.4.2 code, without a fake /vuln handler.
- **PASS**: admin login through original WonderCMS PHP session; actual reflected HTML attribute injection executes a harmless JavaScript marker in Chromium.
- **PASS**: unprivileged visitor receives 403 for the admin-only Flag and 404 for the native JSON database. Admin browser can access its private per-instance objective.
- **PASS**: destroying and recreating the image changes both private admin passwords and Flag values; both first and second instance tests passed.
- **Measured target runtime image**: 43,536,713 bytes ≈ **41.5 MiB**; **memory snapshot** 15.28 MiB with one PID under CI's 192 MiB / 128 PID limits. This is a snapshot, not concurrent/peak usage.
- **NOT verified**: a normal learner's complete route from discovery to Flag; this test deliberately authenticates as administrator to prove original browser XSS. A victim-visiting mechanism, if required by this scenario, belongs to the **challenge itself** (not Worker). The CMS's XSS→plugin installation→RCE path is also not part of this single-Flag exercise.

**Lab skill status:** reflected XSS browser execution verified. **Challenge readiness:** partial because the player's Flag acquisition is not proven; `.release-blocked` remains. The Web backend checks Flag submissions (`attemptChallenge()`), and Worker only schedules target containers. For a *direct-Flag XSS* exercise, don't artificially require a Worker Bot; either redesign a self-contained target proof or choose a public unauthenticated XSS.

## Platform boundary (verified against the actual attackbox repository)

- `attackbox/web/server/services/challenges.ts`: `attemptChallenge()` validates user-submitted answers against Web-side stage flags.
- `attackbox/worker/node/targets/`: scheduling, lifecycle, Docker network, resource isolation, opaque environment variable forwarding; **no Flag judge and no administrator/browser bot**.
- This lab's native PHP endpoint already returns a Flag to an **authenticated administrator**. That is *not* proof that an unauthenticated learner can reach the objective. Simply changing it to return the Flag to everyone bypasses the XSS entirely.
- See [project architecture responsibility contract](../../docs/PLATFORM_FLAG_BOUNDARIES.md); the platform Web backend, not Worker, is responsible for recording submissions.
