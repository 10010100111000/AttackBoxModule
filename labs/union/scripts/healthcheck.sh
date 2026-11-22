#!/bin/sh
set -eu
mariadb-admin --socket=/run/mysqld/mysqld.sock ping --silent >/dev/null
curl -fsS --max-time 3 http://127.0.0.1/ | grep -F 'Player Eligibility Check' >/dev/null
curl -fsS --max-time 3 http://127.0.0.1/challenge.php | grep -F 'Qualifier Challenge' >/dev/null
pidof sshd >/dev/null
pidof php-fpm83 >/dev/null
iptables -S INPUT | grep -F -- '-P INPUT DROP' >/dev/null
