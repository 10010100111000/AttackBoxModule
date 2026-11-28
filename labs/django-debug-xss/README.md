# Harbor Registry — real Django 1.11.4 reflected XSS (CVE-2017-12794)

**Status: authentic Django 1.11.4 and patched 1.11.5 browser comparison passed in CI; the new complete per-instance Flag rotation CI is the release gate.** Not yet released to the platform.

## Source fidelity

- Upstream Django: 1.11.4 is affected; 1.11.5 fixes the unsafe HTML rendering in technical 500 debug pages.
- Vulhub reproduction: https://github.com/vulhub/vulhub/tree/master/django/CVE-2017-12794
- Django advisory: https://www.djangoproject.com/weblog/2017/sep/05/security-releases/
- The real injection sink is **the unmodified vulnerable Django framework's error-page rendering**, not the custom web application.
- The app creates a genuine PostgreSQL unique-constraint exception on duplicate registration using `User.objects.create(username=request.GET['username'])`.
- Adaptation from Vulhub: the model's `max_length` increases from 32 to 512 for a realistic standalone proof-to-Flag JavaScript chain. The backend remains a native PostgreSQL unique constraint and Django's original debug page; **no artificial XSS echo endpoint or simulated traceback is used**.

## Challenge and writeup

The learner-facing Challenge is [Harbor Registry](../../challenges/xss/harbor-registry/HarborRegistry.md). It uses this one Lab image and one Web Flag. The discovery-led solution is in [writeup.md](writeup.md).

## Player experience

A public community registry provides profile registration and a separate editorial submissions page. Players enumerate pages, observe that usernames are unique, explore unexpected registration errors, and submit profile URLs for review. This is not a standalone alert-box proof.

Targeted learning path:

1. Discover the normal registration functionality.
2. Register a handle; retry it and observe a genuine Django/PostgreSQL error.
3. Identify a framework-level reflected XSS in Django 1.11.4's technical 500 page.
4. Submit a crafted URL through the normal editorial workflow.
5. The in-container headless administrator browser logs into the native Django session and follows the submitted path.
6. The XSS executes in that authenticated browser, fetches the editorial-only Flag through a protected endpoint, and sends it to the player's listener on the same private training network.

The Worker **only** starts/stops the target image and attaches the instance-private network; it has no bot, browser, Flag-reading, or judging logic. The Web backend remains responsible for answer validation.

## One-target-container layout

- Python 3.9 / Django 1.11.4: web application and original framework XSS.
- PostgreSQL (local, 127.0.0.1): genuine duplicate-key error.
- Chromium, launched in headless mode through Pyppeteer: editorial browser, as the separate unprivileged `reviewbot` user.
- Django's own database-backed session cookie: authenticated editor, not a hardcoded browser token.
- Release Flag is stored in `labs/django-debug-xss/flags/user.txt` and copied into `/run/django/editorial.flag` during initialization. It is readable only by the web application account; the bot obtains it **only through the authenticated browser session**, never via filesystem reads. The Challenge answer and image seed use the same committed release value; a future release must rotate both together.
- Editor password and Django signing secret generated per instance and kept in access-controlled files, not static source constants.
- Queue stored under `/run/django/reports`, and a fresh browser profile used for each review.
- Container reset destroys the PostgreSQL data, session database, review queue and Flag. No volumes are required.

**Threat model:** Headless Chromium is launched with `--no-sandbox` in default Docker CI because the container runtime does not provide the Chromium user-namespace sandbox. The browser runs as non-root; the entire target must remain unprivileged, without host mounts, Docker socket, or public vulnerable port. This is a known defense-in-depth tradeoff that the actual Worker deployment must review.

## Build and validation

```sh
docker build --build-arg DJANGO_VERSION=1.11.4 -t ttp-django-debug:dev labs/django-debug-xss
docker network create --internal django-lab
docker run -d --name django-target --network django-lab --memory 512m \
  --cpus 1 --pids-limit 256 ttp-django-debug:dev
```

Connect the player's AttackBox to the same instance-private network. The browser callback needs a reachable learner listener; the CI creates the short DNS alias `a` only within its disposable network. The production AttackBox callback hostname/address should come from the real lab network, not a hardcoded public endpoint.

### Independent CI gates

GitHub Actions tests two independent configurations:

- **Vulnerable Django 1.11.4:** a real browser must execute injected JavaScript in the genuine Django error page and the independent learner must receive the private Flag through the editor session.
- **Patched Django 1.11.5:** the identical error input must still cause PostgreSQL integrity failure, but JavaScript execution and Flag callback must not occur.
- All tests use separately networked test containers; the attacker does not mount target files or know the editor password.
- CI measures the actual target image size and memory snapshot and recreates each instance with a different Flag to validate reset semantics.

## Release boundary

The source-level browser and callback chain is testable without Worker-specific business logic. Keep `.release-blocked` until the final CI is green and actual Worker network/resource isolation, callback routing, and platform Flag-validation compatibility have been reviewed. CI success alone does not imply production deployment success.
