#!/bin/bash
set -u
check_http() { curl -fsS -m 5 -H "Host: $1" "http://127.0.0.1$2" >/dev/null; }
check_mysql() { mariadb-admin --protocol=socket ping --silent >/dev/null 2>&1; }
fail=0
check_http devvortex.htb / || { echo 'FAIL: main website' >&2; fail=1; }
check_http dev.devvortex.htb /administrator/ || { echo 'FAIL: Joomla administrator' >&2; fail=1; }
curl -fsS -m 5 -H "Host: dev.devvortex.htb" -H "Accept: application/vnd.api+json" "http://127.0.0.1/api/index.php/v1/config/application?public=true" >/dev/null || { echo "FAIL: Joomla webservice endpoint" >&2; fail=1; } || { echo 'FAIL: Joomla webservice endpoint' >&2; fail=1; }
check_mysql || { echo 'FAIL: MariaDB' >&2; fail=1; }
if [[ "$fail" == 0 ]]; then echo 'healthy: nginx + Joomla/PHP + MariaDB'; else exit 1; fi
