#!/bin/sh
set -eu
if [ -n "${SOCCER_USER_FLAG:-}" ]; then
 case "$SOCCER_USER_FLAG" in *[!A-Za-z0-9_{}]* ) echo "Invalid flag format" >&2; exit 1;; esac
 printf '%s\n' "$SOCCER_USER_FLAG" > /home/player/user.txt
 chmod 0400 /home/player/user.txt
fi
unset SOCCER_USER_FLAG
mkdir -p /run/mysqld /run/php /data/mysql /var/www/html/tiny/uploads
chown mysql:mysql /run/mysqld /data/mysql
chown www-data:www-data /var/www/html/tiny/uploads
if [ ! -d /data/mysql/mysql ]; then
 mariadb-install-db --user=mysql --datadir=/data/mysql --skip-test-db >/dev/null
fi
mariadbd --user=mysql --datadir=/data/mysql --socket=/run/mysqld/mysqld.sock --bind-address=127.0.0.1 --port=3306 &
mysql_pid=$!
i=0
until mariadb-admin ping --socket=/run/mysqld/mysqld.sock --silent >/dev/null 2>&1; do
 i=$((i+1)); if [ "$i" -ge 60 ]; then exit 1; fi
 sleep 1
done
mariadb --socket=/run/mysqld/mysqld.sock < /opt/soccer/init.sql
flag=$(cat /home/player/user.txt)
mariadb --socket=/run/mysqld/mysqld.sock soccer_db -e "UPDATE accounts SET goal = '$flag' WHERE username = 'player'"
php-fpm8.2 -F &
php_pid=$!
su -s /bin/sh -c "exec /usr/local/bin/node /opt/soccer/server.js" soccerapp &
node_pid=$!
nginx -g 'daemon off;' &
nginx_pid=$!
cleanup() {
 kill "$nginx_pid" "$node_pid" "$php_pid" "$mysql_pid" 2>/dev/null || true
 wait "$nginx_pid" "$node_pid" "$php_pid" "$mysql_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
wait "$nginx_pid"
