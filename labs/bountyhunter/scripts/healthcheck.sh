#!/bin/sh
set -eu
curl -fsS --max-time 3 http://127.0.0.1/ | grep -F 'BOUNTY HUNTERS' >/dev/null
curl -fsS --max-time 3 http://127.0.0.1/log_submit.php | grep -F 'Bounty Report System - Beta' >/dev/null
pidof sshd >/dev/null
pidof php-fpm83 >/dev/null
test -r /var/www/localhost/htdocs/db.php
