# Cursed Stale Policy

Status: existing Fastify/Redis/Chromium application is being brought under an independent full-chain E2E. The intended issue is a cached CSP nonce reused across responses; do not mark the advanced XSS objective complete until the real browser returns the exact per-instance Flag.

## Learning objective

Investigate a CSP analysis service that accepts a script payload for review by an administrator browser. The player must discover how the policy is generated and exposed, then understand the effect of reusing a CSP nonce across responses.

The vulnerable behavior uses real components: Fastify serves the CSP analyser and review routes; Redis stores the cached CSP header, review payloads and callback request history; Bull queues review jobs; Puppeteer launches the installed Chromium browser; the review browser receives a readable administrator Flag cookie and opens the target's XSS review route.

This is an intentionally vulnerable training application, not a claim that a third-party product CVE is being reproduced.

## Build and run

~~~sh
docker build -t ttp-cursed-stale-policy -f labs/cursed-stale-policy/Dockerfile labs/cursed-stale-policy
docker run -d --name cursed-stale-policy --memory 1536m --cpus 2 --pids-limit 384 --security-opt no-new-privileges -e CSP_ADMIN_FLAG='TTP{example_admin_flag}' -p 127.0.0.1:8000:8000 ttp-cursed-stale-policy
docker inspect -f '{{.State.Health.Status}}' cursed-stale-policy
~~~

The image contains the default development Flag. When CSP_ADMIN_FLAG is supplied, the entrypoint writes that instance's Flag to /flag.txt before starting Redis, Fastify and the review worker. The variable is then removed from the child-process environment.

## Attack-chain acceptance

The dedicated GitHub Actions workflow builds the image and runs an independent player container on an internal-only Docker network. The player checks nonce reuse across pages, reads the cached policy through the public WebSocket action, submits a nonce-bearing review payload, waits for target-local Puppeteer/Chromium, and retrieves the administrator cookie through the application's callback log. The chain is repeated against two clean instances with different random Flags.

The review queue stores each payload under its own job ID before dispatch, so concurrent submissions cannot silently replace one another. The Fastify process and Bull worker share the queue definition, but only the worker process launches Chromium.

## Scope

This is a Web-only exercise. It does not require Linux privilege escalation, container escape, or Worker integration. The release marker is not removed by Lab E2E; platform lifecycle and grading remain separate.