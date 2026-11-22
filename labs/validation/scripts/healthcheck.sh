#!/bin/sh
set -eu
mariadb-admin --socket=/run/mysqld/mysqld.sock ping --silent >/dev/null
curl --fail --silent --max-time 3 http://127.0.0.1/ | grep -Fq 'Join the UHC - September Qualifiers'
test "$(curl --silent --max-time 3 http://127.0.0.1/config.php | wc -c)" = 0
pidof php-fpm83 >/dev/null
pidof sshd >/dev/null
