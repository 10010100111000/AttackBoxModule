#!/bin/bash
set -euo pipefail
require_private=$(printenv UNION_REQUIRE_PRIVATE_FLAGS || true)
user_flag=$(printenv UNION_STATIC_USER_FLAG || true)
root_flag=$(printenv UNION_STATIC_ROOT_FLAG || true)
qualifier=$(printenv UNION_QUALIFIER_FLAG || true)
if [ "$require_private" = 1 ] && { [ -z "$user_flag" ] || [ -z "$root_flag" ]; }; then
  echo 'Union: both private user/root flags are required' >&2
  exit 1
fi
if [ -z "$qualifier" ]; then
  qualifier="UHC{$(openssl rand -hex 16)}"
fi
if ! [[ "$qualifier" =~ ^UHC\{[a-zA-Z0-9_-]+\}$ ]]; then
  echo 'Union: qualifier must be a safe UHC{...} string' >&2
  exit 1
fi
if [ -n "$user_flag" ]; then
  umask 077
  printf '%s\n' "$user_flag" > /home/uhc/user.txt
fi
if [ -n "$root_flag" ]; then
  umask 077
  printf '%s\n' "$root_flag" > /root/root.txt
fi
chown uhc:uhc /home/uhc/user.txt
chmod 0640 /home/uhc/user.txt
chown root:root /root/root.txt
chmod 0600 /root/root.txt
unset require_private user_flag root_flag
unset UNION_REQUIRE_PRIVATE_FLAGS UNION_STATIC_USER_FLAG UNION_STATIC_ROOT_FLAG UNION_QUALIFIER_FLAG

mkdir -p /run/mysqld /run/nginx /run/sshd
chown mysql:mysql /run/mysqld /var/lib/mysql
if [ ! -d /var/lib/mysql/mysql ]; then
  mariadb-install-db --user=mysql --datadir=/var/lib/mysql --skip-test-db >/dev/null
fi
mariadbd --user=mysql --datadir=/var/lib/mysql \
  --socket=/run/mysqld/mysqld.sock --pid-file=/run/mysqld/mysqld.pid &
mariadb_pid=$!

for attempt in $(seq 1 90); do
  if mariadb-admin --socket=/run/mysqld/mysqld.sock ping --silent >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$mariadb_pid" 2>/dev/null; then
    echo 'Union: MariaDB exited during startup' >&2
    exit 1
  fi
  sleep 1
done
mariadb-admin --socket=/run/mysqld/mysqld.sock ping --silent >/dev/null

# Genuine one-column database tables and FILE privilege, not an SQL emulator.
mariadb --socket=/run/mysqld/mysqld.sock --user=root <<SQL
DROP DATABASE IF EXISTS november;
CREATE DATABASE november CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE TABLE november.players (player VARCHAR(255) NOT NULL);
INSERT INTO november.players(player) VALUES
  ('ippsec'), ('celesian'), ('big0us'), ('luska'), ('tinyboy');
CREATE TABLE november.flag (one VARCHAR(128) NOT NULL);
INSERT INTO november.flag(one) VALUES ('$qualifier');
CREATE USER IF NOT EXISTS 'uhc'@'localhost' IDENTIFIED BY 'uhc-11qual-global-pw';
CREATE USER IF NOT EXISTS 'uhc'@'127.0.0.1' IDENTIFIED BY 'uhc-11qual-global-pw';
ALTER USER 'uhc'@'localhost' IDENTIFIED BY 'uhc-11qual-global-pw';
ALTER USER 'uhc'@'127.0.0.1' IDENTIFIED BY 'uhc-11qual-global-pw';
GRANT SELECT ON november.* TO 'uhc'@'localhost';
GRANT SELECT ON november.* TO 'uhc'@'127.0.0.1';
GRANT FILE ON *.* TO 'uhc'@'localhost';
GRANT FILE ON *.* TO 'uhc'@'127.0.0.1';
FLUSH PRIVILEGES;
SQL
unset qualifier

# Fail closed unless NET_ADMIN works in this isolated network namespace.
iptables -F INPUT
iptables -P INPUT ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -P INPUT DROP

ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -D -e &
sshd_pid=$!
php-fpm83 -F &
php_pid=$!
nginx -g 'daemon off;' &
nginx_pid=$!
cleanup() {
  kill "$nginx_pid" "$php_pid" "$sshd_pid" "$mariadb_pid" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT
wait -n "$nginx_pid" "$php_pid" "$sshd_pid" "$mariadb_pid"
echo 'Union: a required service exited' >&2
exit 1
