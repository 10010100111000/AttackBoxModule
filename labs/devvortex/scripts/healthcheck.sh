#!/bin/bash
set -u
check_http() { curl -fsS -m 3 -H "Host: $1" "http://127.0.0.1$2" >/dev/null; }
check_mysql() { mariadb-admin --protocol=socket ping --silent >/dev/null 2>&1; }
check_ssh() { timeout 3 bash -c 'exec 3<>/dev/tcp/127.0.0.1/22; IFS= read -r line <&3; [[ "$line" == SSH-2.0-* ]]' 2>/dev/null; }
fail=0
check_http devvortex.htb / || { echo 'FAIL: main website' >&2; fail=1; }
check_http dev.devvortex.htb /administrator/ || { echo 'FAIL: Joomla administrator' >&2; fail=1; }
check_mysql || { echo 'FAIL: MariaDB' >&2; fail=1; }
check_ssh || { echo 'FAIL: SSH' >&2; fail=1; }
if [[ "$fail" == 0 ]]; then echo 'healthy: nginx + Joomla/PHP + MariaDB + SSH'; else exit 1; fi
