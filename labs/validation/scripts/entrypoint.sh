#!/bin/bash
set -euo pipefail
user_flag=$(printenv VALIDATION_STATIC_USER_FLAG || true)
root_flag=$(printenv VALIDATION_STATIC_ROOT_FLAG || true)
need_private=$(printenv VALIDATION_REQUIRE_PRIVATE_FLAGS || true)
if [ "$need_private" = 1 ] && { [ -z "$user_flag" ] || [ -z "$root_flag" ]; }; then
  echo 'Validation: both user and root private flags must be provided' >&2
  exit 1
fi
# Do not bake the credential into a publicly distributed image.
db_pass=$(printenv VALIDATION_DB_PASSWORD || true)
if [ -z "$db_pass" ]; then
  db_pass=$(openssl rand -hex 16)
fi
if ! [[ "$db_pass" =~ ^[a-zA-Z0-9_-]{10,64}$ ]]; then
  echo 'Validation: database credential must be a 10-64 character alphanumeric secret' >&2
  exit 1
fi
printf 'root:%s\n' "$db_pass" | chpasswd
# The original challenge has a web-accessible PHP config source. PHP executes
# it, while a real MariaDB FILE read can disclose it.
printf '%s\n' '<?php' \
  '$servername = "127.0.0.1";' \
  '$username = "uhc";' \
  "\$password = \"$db_pass\";" \
  '$dbname = "registration";' \
  'mysqli_report(MYSQLI_REPORT_OFF);' \
  '$conn = new mysqli($servername, $username, $password, $dbname);' \
  'if ($conn->connect_errno) { http_response_code(503); exit("Service unavailable"); }' \
  > /var/www/html/config.php
chown root:root /var/www/html/config.php
chmod 0644 /var/www/html/config.php
if [ -n "$user_flag" ]; then
  printf '%s\n' "$user_flag" > /home/htb/user.txt
fi
if [ -n "$root_flag" ]; then
  printf '%s\n' "$root_flag" > /root/root.txt
fi
chown htb:htb /home/htb/user.txt
chmod 0644 /home/htb/user.txt
chown root:root /root/root.txt
chmod 0600 /root/root.txt
unset user_flag root_flag need_private
unset VALIDATION_DB_PASSWORD VALIDATION_STATIC_USER_FLAG VALIDATION_STATIC_ROOT_FLAG VALIDATION_REQUIRE_PRIVATE_FLAGS

mkdir -p /run/mysqld /run/apache2 /run/php /run/sshd
chown mysql:mysql /run/mysqld /var/lib/mysql
if [ ! -d /var/lib/mysql/mysql ]; then
  mariadb-install-db --user=mysql --datadir=/var/lib/mysql --skip-test-db >/dev/null
fi
mariadbd --user=mysql --datadir=/var/lib/mysql \
  --socket=/run/mysqld/mysqld.sock --pid-file=/run/mysqld/mysqld.pid &
db_pid=$!
for attempt in $(seq 1 75); do
  if mariadb-admin --socket=/run/mysqld/mysqld.sock ping --silent >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$db_pid" 2>/dev/null; then
    echo 'Validation: MariaDB failed to start' >&2
    exit 1
  fi
  sleep 1
done
mariadb-admin --socket=/run/mysqld/mysqld.sock ping --silent >/dev/null

mariadb --socket=/run/mysqld/mysqld.sock --user=root <<SQL
DROP DATABASE IF EXISTS registration;
CREATE DATABASE registration CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE TABLE registration.registration (
 id INT AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(90) NOT NULL,
 userhash CHAR(32) NOT NULL,
 country VARCHAR(1024) NOT NULL,
 regtime BIGINT NOT NULL
);
CREATE USER IF NOT EXISTS 'uhc'@'127.0.0.1' IDENTIFIED BY '$db_pass';
ALTER USER 'uhc'@'127.0.0.1' IDENTIFIED BY '$db_pass';
CREATE USER IF NOT EXISTS 'uhc'@'localhost' IDENTIFIED BY '$db_pass';
ALTER USER 'uhc'@'localhost' IDENTIFIED BY '$db_pass';
GRANT SELECT,INSERT ON registration.* TO 'uhc'@'127.0.0.1';
GRANT SELECT,INSERT ON registration.* TO 'uhc'@'localhost';
GRANT FILE ON *.* TO 'uhc'@'127.0.0.1';
GRANT FILE ON *.* TO 'uhc'@'localhost';
FLUSH PRIVILEGES;
SQL
unset db_pass
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -D -e &
ssh_pid=$!
php-fpm83 -F &
php_pid=$!
httpd -DFOREGROUND &
http_pid=$!
cleanup() {
  kill "$http_pid" "$php_pid" "$ssh_pid" "$db_pid" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT
wait -n "$http_pid" "$php_pid" "$ssh_pid" "$db_pid"
echo 'Validation: a required service unexpectedly exited' >&2
exit 1
