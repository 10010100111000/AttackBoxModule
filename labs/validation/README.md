# Validation — UHC September Qualifiers (Linux Easy)

Independently reconstructed from the retired 2021 Hack The Box machine by IppSec. This is not an official HTB image and the original unpublished PHP sources are not reproduced verbatim. Apache/PHP, MariaDB, SQL injection, filesystem privileges and Linux user authentication are genuine.

## Player discovery progression

1. Nmap shows web HTTP :80 and OpenSSH :22. The public web page is a normal UHC September Qualifiers registration form; the Country field is a browser dropdown.
2. POST of username/country performs a *prepared* INSERT into the real MariaDB registration table, issues a cookie containing md5(username) and redirects to /account.php.
3. account.php retrieves that row safely by cookie, but uses the previously saved country unsafely in a **different SELECT** query. This is a real second-order SQL injection — not a query-string-only login bypass.
4. One-column UNION queries return country registration names from MariaDB. The DB account is intentionally granted the FILE privilege. Genuine LOAD_FILE can read web application source.
5. The database service user can write into /var/www/html through real Unix filesystem permissions, enabling SELECT ... INTO OUTFILE with the real MariaDB engine. Files appear on Apache; if PHP is written, the PHP-FPM handler executes it.
6. The web app PHP configuration holds the same password used by the real root Unix account. User flag is /home/htb/user.txt (world readable, as in the original); root flag is /root/root.txt (root-only).

### Fidelity

The original had Debian/Ubuntu services, MariaDB 10.5, Apache 2.4.48, PHP 7.4, and auxiliary ports 4566/8080. This compact reproduction uses Alpine 3.20, Apache, PHP 8.3 FPM, real MariaDB, shadow/password-based su and SSH. The two extra broken ancillary HTTP services from the original are omitted rather than faked. The frontend follows the historic Bootstrap-style UHC form and account page, locally styled without requiring CDN requests.

The original site source was not published, so routing, forms, session and SQL behavior are reconstructed from publicly observed responses, not copied original code.

References:
- https://pencer.io/ctf/ctf-htb-validation/
- https://fahmifj.github.io/ctf/hackthebox/validation/
- https://0xdf.gitlab.io/2021/09/14/htb-validation.html

## Build and isolated use

From repository root:

    docker build -f labs/validation/Dockerfile -t ttp-validation:dev labs/validation

No public host port, privileged mode, host network, or host mount:

    docker network create --internal validation-lab
    docker run -d --name validation-target --network validation-lab \
      --memory 256m --pids-limit 192 \
      -e VALIDATION_REQUIRE_PRIVATE_FLAGS=1 \
      -e VALIDATION_STATIC_USER_FLAG='TTP{your_test_user_flag}' \
      -e VALIDATION_STATIC_ROOT_FLAG='TTP{your_test_root_flag}' \
      ttp-validation:dev

The root/database credential is randomized at each boot by default and written to the actual config.php file at runtime. It is not baked into a public image. You may set VALIDATION_DB_PASSWORD in CI or Worker for deterministic fixtures (10-64 alphanumeric, underscore or hyphen). For production, keep it generated and private to the instance. The two flags must be independently injected by the Worker and never included as production values in the image or Git history. The default demo filesystem is reset when the container is deleted and recreated with no volumes.

CI tests actual PHP handling (no raw config.php served), prepared registration inserts, cookie and account view, real second-order UNION expression, MariaDB LOAD_FILE reading of an existing non-sensitive OS file, runtime PHP config disclosure via database, and native INTO OUTFILE writing of an ordinary text file into the real Apache document root. It also checks isolated containers and reset. These tests are not substitutes for an independent full local user-to-root end-to-end exploit verification.

### Security

This service is intentionally vulnerable and must only run on dedicated per-user internal challenge networks. No ingress from the public Internet and no access to platform services or other learners. Database FILE privilege, writable document root, and the reused root account password are specific to this isolated challenge, never platform defaults. This target does not require privileged Docker, NET_ADMIN, a host Docker socket, or an external database.
