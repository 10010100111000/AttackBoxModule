#!/usr/bin/env bash
set -euo pipefail
test "$(dpkg-query -W -f='${Version}' zoneminder)" = '1.29.0+dfsg-1ubuntu2'
test -f /usr/share/zoneminder/www/ajax/log.php
grep -Fq '$limit = isset($_POST[' /usr/share/zoneminder/www/ajax/log.php
grep -Fq '$sql .= " order by ".$sortField." ".$sortOrder." limit ".$limit;' /usr/share/zoneminder/www/ajax/log.php
test -f /usr/share/zoneminder/www/index.php
dpkg-query -W -f='${Version}' mysql-server-5.7 | grep -Eq '^5[.]7[.]'
grep -Eq '^[[:space:]]*Alias[[:space:]]+/zm[[:space:]]' /etc/apache2/conf-enabled/zoneminder.conf
echo 'PASS: authentic ZoneMinder 1.29.0 package and vulnerable source'
