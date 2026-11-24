#!/bin/sh
set -eu

mariadb-admin --protocol=socket --socket=/run/mysqld/mysqld.sock -uroot ping --silent >/dev/null
curl -fsS -H 'Host: trick.htb' http://127.0.0.1/ | grep -Fq 'Coming Soon'
curl -fsS -H 'Host: preprod-payroll.trick.htb' http://127.0.0.1/ | grep -Fq 'Payroll Management System'
curl -fsS -H 'Host: preprod-marketing.trick.htb' http://127.0.0.1/ | grep -Fq 'Technology that moves your business forward'
dig @127.0.0.1 trick.htb SOA +short | grep -Fq 'trick.htb.'
dig @127.0.0.1 axfr trick.htb | grep -Fq 'preprod-payroll.trick.htb.'
target_ip="$(cat /run/trick-target-ip)"
dig -x "$target_ip" @127.0.0.1 +short | grep -Fxq 'trick.htb.'
fail2ban-client ping >/dev/null
fail2ban-client status sshd >/dev/null
kill -0 "$(cat /run/mysqld/mysqld.pid)"
pidof named >/dev/null
pidof nginx >/dev/null
pidof php-fpm84 >/dev/null
pidof sshd >/dev/null
