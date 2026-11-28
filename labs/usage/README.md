# Usage — Laravel password recovery SQLi and admin upload reconstruction

**Status:** independent full-chain lab CI passed on 2026-11-24 ([evidence](https://github.com/10010100111000/AttackBoxModule/actions/runs/45386437038)). Production release remains blocked pending actual platform deployment and isolation checks. This is an independent training reconstruction, not the original HTB source or image.

## Learning goals

- `sqli.boolean-blind`: infer data from true/false responses in a normal Laravel password-recovery flow.
- `sqli.time-blind`: demonstrate a real MySQL `SLEEP()` timing oracle separately from the boolean oracle.
- `sqli.db-enumeration`: extract the Laravel-admin account hash from the same MySQL database.
- `file_upload.unrestricted-upload`: exploit the actual vulnerable Laravel-admin Image field and PHP handling.
- Linux foothold and credential reuse: obtain the real `dash` shell, inspect Monit configuration, authenticate as `xander`.
- Root objective: use the genuine p7zip 16.02 `@listfile` behavior through a sudo rule to read the protected Root Flag.

## Training fidelity and documented differences

The original Usage application source was not published. The main Laravel application routes and UI in this reconstruction are therefore **independently rebuilt from public writeups and observed request shapes**, not represented as the original source. The vulnerable query uses the real Laravel 10.18.0 framework and genuine MySQL 8.0; it is not a mock SQL parser or a payload-matching endpoint.

- Main stack: Laravel Framework 10.18.0, PHP 8.1, MySQL Community Server 8.0.46.
- Admin stack: actual `encore/laravel-admin` 1.8.19 package, pinned to the affected release. The package source's internal `Admin::VERSION` string may report 1.8.17; the Composer package version is the pinned 1.8.19 release. Do not confuse the UI's constant with the package release metadata.
- The public HTB writeups disagree on the Laravel-admin version label (1.8.17 / 1.8.19); the package vulnerability advisory identifies versions through 1.8.19 as affected. The implementation uses 1.8.19 and tests its actual upload field.
- The original HTB private `usage_management` helper is not available. The Root-stage adaptation therefore uses the **real p7zip 16.02 binary directly**, with a deliberately unsafe sudo command that preserves the same wildcard-to-`@listfile` parsing primitive. This is an explicitly documented reconstruction difference, not a claim that the original private helper was recovered.
- Monit, SSH, PHP-FPM, nginx and MySQL are real processes inside one Docker target. MySQL listens only on loopback. No Docker socket, host mount, privileged mode, or host-root access is used.

## Original evidence

- HTB Usage: https://www.hackthebox.com/machines/usage
- IppSec walkthrough: https://www.youtube.com/watch?v=cx9Da-PoXG4
- Independent writeup: https://www.cipherbuu.net/posts/Usage-Walkthrough/
- Independent writeup: https://www.brunorochamoura.com/posts/usage/
- Laravel-admin advisory / CVE-2023-24249: https://github.com/advisories/GHSA-58rr-37rr-r6h5
- Vulnerable Laravel-admin source commit: https://github.com/z-song/laravel-admin/commit/6c292ebb5efa886fa4776d86e975180608505946

## Reusable Challenges

This Lab is shared by four learner-facing Challenges; they all use the same Usage image and per-instance target:

- [Usage](../../challenges/startpoint/usage/Usage.md): integrated User and Root path.
- [Blind Recovery](../../challenges/sql-injection/11-usage/blind-recovery.md): focused boolean/time blind SQLi objective.
- [Admin Avatar Upload](../../challenges/file-security/usage/admin-avatar-upload.md): focused Laravel-admin upload objective.
- [7za Listfile](../../challenges/linux-privilege-escalation/usage/7za-listfile.md): focused xander-to-root privilege objective.

The focused Challenges reuse the integrated Lab's User or Root Flag; they do not create separate target images or additional instances.

Detailed discovery-led solution: [writeup.md](writeup.md).

## Player discovery path

1. Add the target IP to `/etc/hosts` as `usage.htb` and `admin.usage.htb`.
2. Browse the normal Daily Blogs site; register a normal user.
3. Discover the password recovery form and submit an email address.
4. Compare true/false responses and use the real `POST /forget-password` `email` parameter for blind extraction. The form has Laravel's genuine CSRF token.
5. Extract and crack the `admin_users.password` bcrypt hash.
6. Visit `http://admin.usage.htb/auth/login` and authenticate to the actual Laravel-admin package.
7. Use the built-in `/auth/setting` avatar Image field. The vulnerable upstream package accepts the image/PHP polyglot under the original filename and stores it below the public uploads directory.
8. Obtain a shell as the real `dash` PHP-FPM user, retrieve its SSH key and User Flag.
9. Read `/home/dash/.monitrc`; the Monit password is reused by the real `xander` system account.
10. Use SSH as xander and investigate the allowed sudo 7za command. The actual p7zip 16.02 listfile behavior can disclose `/root/root.txt`.

## Single-container layout

One Docker image runs:
- MySQL Community Server 8.0.46 (127.0.0.1 only)
- Laravel 10.18.0 + PHP-FPM 8.1
- Laravel-admin 1.8.19
- nginx
- OpenSSH
- Monit
- p7zip 16.02

The app database is `usage_blog`. It contains the normal Laravel `users` table and Laravel-admin's `admin_users` table. The SQLi DB account is a real MySQL user restricted to the local database. The player does not receive database credentials through the challenge UI.

## Build and isolated run

From repository root:

```sh
docker build -f labs/usage/Dockerfile -t ttp-usage:dev labs/usage
docker network create --internal usage-lab
docker run -d --name usage-target --network usage-lab \
  --network-alias usage.htb --network-alias admin.usage.htb \
  --memory 768m --cpus 1 --pids-limit 256 \
  -e USAGE_REQUIRE_PRIVATE_FLAGS=1 \
  -e USAGE_STATIC_USER_FLAG='TTP{private_user_flag}' \
  -e USAGE_STATIC_ROOT_FLAG='TTP{private_root_flag}' \
  ttp-usage:dev
docker inspect -f '{{.State.Health.Status}}' usage-target
```

Do not publish ports publicly. The platform's private target network should provide the two hostnames to the player's AttackBox. MySQL and Monit remain loopback-only.

## Flag and reset

Worker passes `USAGE_STATIC_USER_FLAG` and `USAGE_STATIC_ROOT_FLAG` as opaque environment variables. The entrypoint writes them to `/home/dash/user.txt` (root:dash, 0640) and `/root/root.txt` (root:root, 0600). Web backend judges the static values; Worker only starts/stops the container.

No data volume is declared. Deleting the target container removes its MySQL database, uploaded files, SSH keys, session state, and generated system credentials. A new instance receives new Worker-supplied flags and fresh generated credentials.

## CI acceptance

The independent attacker container must prove:
1. normal registration and password recovery work;
2. boolean true/false responses differ;
3. a MySQL `SLEEP()` condition produces a measurable timing difference;
4. the actual bcrypt hash is extracted through blind SQLi and cracked offline;
5. the actual Laravel-admin login and profile upload route accepts the polyglot;
6. the uploaded PHP file executes as `dash`;
7. the SSH private key is obtained through that shell and used to log in as dash;
8. the Monit credential is reused for xander;
9. real sudo p7zip 16.02 `@listfile` behavior discloses the protected Root Flag;
10. a second fresh container has a different Flag pair and no prior state.

Acceptance requires real components, genuine vulnerability behavior and a verified end-to-end learning path, not identical private source code. A passing lab CI does not prove the real Worker deployment or platform answer configuration. Keep `.release-blocked` until those are separately checked.
