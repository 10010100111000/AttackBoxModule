# ImpressCMS 1.4.2 — shared multi-Challenge target

**Status:** first container implementation in progress. Not built, functionally accepted, Worker-verified or released.

## Target model

One target template, slug **impresscms**, will serve multiple independent Challenges. The target uses the pinned ImpressCMS 1.4.2 core plus a provisional Content module source candidate. Every Challenge will bind to the same target template and have its own category, difficulty, prompt, hint, answer/Flag and learner progress.

The CMS state is shared by Challenges on the same per-user target instance. Challenges must not delete or overwrite data needed by other Challenges. Stop/start persistence and reset behavior must be recorded before publishing the Challenge set.

## Pinned sources

| Component | Source | Revision | Status |
|---|---|---|---|
| ImpressCMS core | https://github.com/ImpressCMS/impresscms | tag v1.4.2, commit 56caca0356646ad29497ce877589326a4a76123b | pinned |
| Content add-on | https://github.com/IPFModules/content | commit 1a6395e6d5f85f39ee241987bc0de89a1dc9117e | provisional; tag metadata says 1.3 Beta and is not confirmed as official Content 1.2.1 Final |

The Content add-on must be replaced or confirmed against the exact official package before release. See docs/research/IMPRESSCMS_1.4.2_SOURCE_AUDIT.md.

## Runtime design

- PHP 7.4 FPM + Nginx.
- MariaDB runs in the same target container, supervised with PHP-FPM and Nginx.
- Database and CMS are initialized on first container start using the upstream installer flow.
- The CMS URL is set to the target container's current private IP.
- Runtime data lives in the container filesystem. A new target instance starts from a clean image and reinitializes the database.
- PHP application code is root-owned after installation; only upload, cache, template-cache and trust directories remain writable by the web process.
- Healthcheck verifies the public homepage and an actual database query.

## Build and local smoke

    docker build -t ttp-impresscms:local -f labs/impresscms/Dockerfile labs/impresscms

    docker run -d --name impresscms-lab \
      --security-opt no-new-privileges \
      --memory 1024m --cpus 1 --pids-limit 192 \
      -p 127.0.0.1:8080:80 \
      ttp-impresscms:local

    docker inspect -f '{{.State.Health.Status}}' impresscms-lab

The initial administrator account is **admin**; its password is set by IMPCMS_ADMIN_PASSWORD (local default: TTP-ImpressCMS-Admin-Only). This is a lab account, not a production credential.

## Functional acceptance scope

CI must only verify:
- image builds;
- container starts and remains healthy;
- homepage and login page render;
- CMS administrator login works with the configured lab account;
- the Content module is present and its ordinary page loads;
- an unauthenticated visitor cannot open the system administration page.

Do not add automated XSS, SQLi, access-control-bypass, path-traversal, PHP-eval, exploit-chain or Flag-extraction tests.

## Known blockers

- Content module source provenance and exact CVE-2021-28088 field mapping are not resolved.
- PHP 7.4 / MariaDB compatibility and the browser installer automation have not been built or tested.
- Single-container resource use is not measured.
- Challenge-specific data and Flags have not yet been seeded.
- The target must remain release-blocked until ordinary application functions are verified.
