#!/bin/sh
set -eu
mariadb-admin --socket=/run/mysqld/mysqld.sock -uroot ping >/dev/null 2>&1
curl -fsS http://127.0.0.1:8080/ >/dev/null
curl -fsS http://127.0.0.1:8080/shop/index.php >/dev/null
