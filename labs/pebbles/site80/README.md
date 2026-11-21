# PG Pebbles: PHP entry page (stage 1)

**Status: behavioral reconstruction only; NOT a completed OffSec Pebbles replica.**

The observed initial HTTP 80 entry point is a simple Pebbles PHP login form, which was not the exploitable SQL injection in multiple independent writeups. The SQLi lives in genuine ZoneMinder 1.29.0 under a discoverable /zm/ path on another Apache listener.

Files:
- public/index.php: PHP login form; optional configured operator account via PEBBLES_LOGIN_USER and PEBBLES_LOGIN_HASH. Default credentials are intentionally absent.
- public/style.css: minimal approximation. Original OffSec page HTML/CSS was not released in the sources checked; pixel accuracy is NOT claimed.
- tests/router.php, tests/smoke.sh: local PHP-server behavior validation. Missing /zm is expected until the genuine application is installed.
- ../apache/pebbles-ports.conf: port 80 and 3305 Apache layout proposal. Not yet integrated or enabled.

Local check from this directory: `bash tests/smoke.sh` (requires PHP CLI and curl).

Next: build and verify actual ZoneMinder 1.29.0, upstream /zm assets, Apache, MySQL, FTP, SSH, and optional Tomcat in one isolated Linux Docker target. Do not introduce any custom simulated CVE endpoint or premature /zm hint.

Original references:
- https://www.juannemina.com/writeups/pebbles-proving-grounds/
- https://walkthroughs.cyanidesecurity.com/proving-grounds/pebbles
- https://medium.com/@0xrave/pebbles-provingground-practice-d2a28edbd22b
- https://github.com/ZoneMinder/zoneminder/tree/v1.29.0

The project's static Flag will be introduced only after a genuine lab exploit acceptance test. Never publish actual static answers into a public repo.
