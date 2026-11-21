#!/bin/sh
set -eu
test -s /var/www/localhost/htdocs/nibbleblog/content/private/users.xml
test -s /home/nibbler/user.txt
test -s /root/root.txt
wget -q -T 3 -O /dev/null http://127.0.0.1/
page=$(wget -q -T 4 -O - http://127.0.0.1/nibbleblog/admin.php)
case "$page" in *Nibbleblog*) : ;; *) exit 1 ;; esac
pidof sshd >/dev/null
