#!/bin/bash
set -euo pipefail
umask 077

user_flag="${TRICK_STATIC_USER_FLAG:-}"
root_flag="${TRICK_STATIC_ROOT_FLAG:-}"
if [[ -z "$user_flag" || -z "$root_flag" ]]; then
  echo "Trick: Worker must inject both private User and Root Flags" >&2
  exit 1
fi
if [[ "$user_flag" == "$root_flag" ]]; then
  echo "Trick: User and Root Flags must be different" >&2
  exit 1
fi

printf '%s\n' "$user_flag" > /home/michael/user.txt
printf '%s\n' "$root_flag" > /root/root.txt
chown michael:michael /home/michael/user.txt
chmod 0644 /home/michael/user.txt
chown root:root /root/root.txt
chmod 0600 /root/root.txt
unset user_flag root_flag TRICK_STATIC_USER_FLAG TRICK_STATIC_ROOT_FLAG

# The target's reverse DNS record follows its actual per-instance address.
target_ip="${TRICK_TARGET_IPV4:-}"
if [[ -z "$target_ip" ]]; then
  target_ip="$(ip -4 -o addr show dev eth0 2>/dev/null | awk 'NR == 1 { sub(/\/.*/, "", $4); print $4 }')"
fi
target_ip="${target_ip:-192.0.2.10}"
if [[ ! "$target_ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
  echo "Trick: invalid target IPv4 address" >&2
  exit 1
fi
IFS=. read -r oct1 oct2 oct3 oct4 <<< "$target_ip"
cat > /var/bind/reverse.zone <<EOF
\$TTL 60
@ IN SOA trick.htb. root.trick.htb. (
  2026112501 60 60 3600 60
)
@ IN NS trick.htb.
$oct4 IN PTR trick.htb.
EOF
cat >> /etc/bind/named.conf <<EOF

zone "$oct3.$oct2.$oct1.in-addr.arpa" {
    type master;
    file "/var/bind/reverse.zone";
    allow-transfer { any; };
};
EOF
chown named:named /var/bind/reverse.zone
printf '%s\n' "$target_ip" > /run/trick-target-ip
chmod 0644 /run/trick-target-ip
named-checkconf /etc/bind/named.conf
named-checkzone "$oct3.$oct2.$oct1.in-addr.arpa" /var/bind/reverse.zone

# Per-boot database and SSH credentials are not baked into the image.
db_pass="$(openssl rand -hex 16)"
ssh_pass="$(openssl rand -hex 20)"
printf 'michael:%s\n' "$ssh_pass" | chpasswd
unset ssh_pass

mkdir -p /home/michael/.ssh /run/mysqld /run/named /run/php-fpm /run/sshd /run/openrc /var/log /var/empty
chown -R michael:michael /home/michael
chmod 0700 /home/michael/.ssh
ssh-keygen -A
ssh-keygen -q -t rsa -b 2048 -N '' -f /home/michael/.ssh/id_rsa
ssh-keygen -y -f /home/michael/.ssh/id_rsa > /home/michael/.ssh/authorized_keys
chown -R michael:michael /home/michael/.ssh
chmod 0600 /home/michael/.ssh/id_rsa /home/michael/.ssh/authorized_keys

chown mysql:mysql /run/mysqld /var/lib/mysql
if [[ ! -d /var/lib/mysql/mysql ]]; then
  mariadb-install-db --user=mysql --datadir=/var/lib/mysql --skip-test-db >/dev/null
fi
mariadbd --user=mysql --datadir=/var/lib/mysql \
  --socket=/run/mysqld/mysqld.sock --pid-file=/run/mysqld/mysqld.pid \
  --bind-address=127.0.0.1 &
db_pid=$!

for attempt in $(seq 1 75); do
  if mariadb-admin --protocol=socket --socket=/run/mysqld/mysqld.sock -uroot ping --silent >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$db_pid" 2>/dev/null; then
    echo "Trick: MariaDB exited during startup" >&2
    exit 1
  fi
  sleep 1
done
mariadb-admin --protocol=socket --socket=/run/mysqld/mysqld.sock -uroot ping --silent >/dev/null

mariadb --protocol=socket --socket=/run/mysqld/mysqld.sock -uroot <<SQL
CREATE DATABASE payroll_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payroll_db;
CREATE TABLE users (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  doctor_id INT NOT NULL DEFAULT 0,
  name VARCHAR(128) NOT NULL,
  type INT NOT NULL DEFAULT 1,
  address VARCHAR(255) NOT NULL DEFAULT '',
  contact VARCHAR(64) NOT NULL DEFAULT '',
  password VARCHAR(255) NOT NULL,
  username VARCHAR(64) NOT NULL
);
INSERT INTO users (doctor_id, name, type, address, contact, password, username)
VALUES (0, 'Administrator', 1, '', '', 'SuperGucciRainbowCake', 'Enemigosss');
CREATE TABLE department (id INT PRIMARY KEY, name VARCHAR(80) NOT NULL);
CREATE TABLE position (id INT PRIMARY KEY, name VARCHAR(80) NOT NULL);
CREATE TABLE employee (id INT PRIMARY KEY, name VARCHAR(120) NOT NULL, department_id INT);
CREATE TABLE attendance (id INT PRIMARY KEY, employee_id INT, work_date DATE);
CREATE TABLE allowances (id INT PRIMARY KEY, name VARCHAR(80), amount DECIMAL(10,2));
CREATE TABLE deductions (id INT PRIMARY KEY, name VARCHAR(80), amount DECIMAL(10,2));
CREATE TABLE payroll (id INT PRIMARY KEY, employee_id INT, period VARCHAR(20));
CREATE TABLE payroll_items (id INT PRIMARY KEY, payroll_id INT, amount DECIMAL(10,2));
CREATE TABLE employee_allowances (employee_id INT, allowance_id INT);
CREATE TABLE employee_deductions (employee_id INT, deduction_id INT);
CREATE USER 'remo'@'127.0.0.1' IDENTIFIED BY '$db_pass';
GRANT SELECT ON payroll_db.* TO 'remo'@'127.0.0.1';
GRANT FILE ON *.* TO 'remo'@'127.0.0.1';
FLUSH PRIVILEGES;
SQL

cat > /var/www/payroll/db_connect.php <<EOF
<?php
mysqli_report(MYSQLI_REPORT_OFF);
\$conn = new mysqli('127.0.0.1', 'remo', '$db_pass', 'payroll_db');
if (\$conn->connect_errno) {
    http_response_code(503);
    exit('Service unavailable');
}
EOF
chown root:root /var/www/payroll/db_connect.php
chmod 0644 /var/www/payroll/db_connect.php
unset db_pass

# OpenSSH logs authentication failures to the local syslog socket.
touch /var/log/messages
syslogd -O /var/log/messages

/usr/sbin/named -u named -g -c /etc/bind/named.conf &
named_pid=$!
php-fpm84 -F &
php_pid=$!
nginx -g 'daemon off;' &
nginx_pid=$!
/usr/sbin/sshd -D &
sshd_pid=$!

# Use the distribution's real OpenRC Fail2ban service.
printf 'rc_sys="docker"\n' > /etc/rc.conf
touch /run/openrc/softlevel
rc-service fail2ban start

for attempt in $(seq 1 30); do
  if fail2ban-client ping >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
fail2ban-client ping >/dev/null
fail2ban-client status sshd >/dev/null

cleanup() {
  rc-service fail2ban stop >/dev/null 2>&1 || true
  for pid in "${sshd_pid:-}" "${nginx_pid:-}" "${php_pid:-}" "${named_pid:-}" "${db_pid:-}"; do
    if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; fi
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

wait -n "$db_pid" "$named_pid" "$php_pid" "$nginx_pid" "$sshd_pid"
echo "Trick: a required service exited unexpectedly" >&2
exit 1
