# Django 1.11.4 debug-page XSS (CVE-2017-12794)

**Status: source_verified / implementation NOT built / no attack-chain CI yet.** This is a candidate for a compact Web XSS specialty challenge, not a completed machine.

## Original source and vulnerability

- Django upstream advisory (2017-09-05): https://www.djangoproject.com/weblog/2017/sep/05/security-releases/
- Fixed by Django 1.11.5; affected release to reproduce: **Django 1.11.4**.
- Vulhub original reproduction: https://github.com/vulhub/vulhub/tree/master/django/CVE-2017-12794
- Original files:
  - `app.py`: `User.objects.create(username=request.GET['username'])`
  - `xss/models.py`: unique, max_length=32 username
  - `docker-compose.yml`: Django container **plus PostgreSQL 9.6**, not SQLite

The genuine vulnerability is in Django's **technical 500 debug-page template** when `DEBUG=True`. The User model and its unique constraint only trigger an exception carrying attacker-supplied input. Do **not** add a separate unescaped echo endpoint and claim that it demonstrates CVE-2017-12794.

## Intended training design

- **Difficulty:** beginner specialty; no SSH, Root Flag, or admin Bot required merely to show reflected JavaScript execution.
- **Entry:** believable public account-registration interface. Players inspect the form, requests, framework clues, and behavior when reusing an identifier; no CVE or exploit path in the public task description.
- **Actual mechanism:** an identifier is stored, then a duplicate insert causes a genuine PostgreSQL unique-constraint exception. Vulnerable Django 1.11.4 renders the technical 500 page. A JavaScript proof must execute in a **real** headless browser, not just appear as a string in HTML.
- **Learning distinction:** unlike the WonderCMS administrator-review challenge, this one teaches an error-page HTML context and a framework-level XSS. It does not inherently provide an administrator privilege boundary. A Flag design must be justified separately; do not award a Flag using an unrelated hardcoded detection handler.

## Container feasibility review (not yet passed)

The Vulhub proof explicitly depends on PostgreSQL error-message behavior. Replacing PostgreSQL with SQLite just to shrink the image is **not approved** until it passes the same black-box execution test. The platform currently schedules one Docker target image per user, so a PostgreSQL implementation would need a supervised local database process in that image, or a worker-supported alternative proven in the actual platform. Both change image and memory costs.

The historical Django version also requires an old compatible Python runtime. Dockerfile must pin the runtime and dependencies and verify that Python/Django/PostgreSQL process startup is reproducible without using deprecated, inaccessible package repositories.

## Required CI before declaring success

1. Build image on linux/amd64; print exact size and process/memory limits.
2. From a separate attacker container, discover and use the real public input, create an account, and cause a PostgreSQL duplicate-key failure; verify that Django itself generated a technical 500 page.
3. Drive a real browser in CI, execute a **benign** JavaScript marker from the actual traceback context. No JS execution => fail, even if source contains a `<script>` string.
4. Run the identical test against **patched Django 1.11.5**, which must not execute the marker.
5. Recreate the target and verify user/database state reset. Check health and absence of unauthorized host mounts, privileged mode, Docker socket, and public port exposure.
6. Only then decide whether the machine has a meaningful platform Flag objective or is better left as a browser-evidence specialty exercise.

## Candidate decision

**source_verified → feasibility pending**. The actual upstream source and affected versions are confirmed, but compact single-image packaging, a meaningful Flag objective, and real CI have not been demonstrated. Do not mark release-ready.
