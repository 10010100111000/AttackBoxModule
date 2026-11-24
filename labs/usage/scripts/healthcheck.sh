#!/bin/bash
set -euo pipefail
mysqladmin --protocol=socket --socket=/var/lib/mysql/mysql.sock \
  -uroot -p"$(cat /var/lib/mysql/.usage-root-password)" ping --silent >/dev/null
curl -fsS -H 'Host: usage.htb' http://127.0.0.1/ | grep -q 'Daily Blogs'
curl -fsS -H 'Host: admin.usage.htb' http://127.0.0.1/auth/login | grep -q 'username'
kill -0 "$(cat /run/sshd.pid)" 2>/dev/null || pgrep -x sshd >/dev/null
