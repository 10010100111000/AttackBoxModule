#!/bin/sh
set -eu
if [ -n "$ZIPPING_USER_FLAG" ]; then
  printf '%s\n' "$ZIPPING_USER_FLAG" > /home/rektsu/user.txt
  chmod 0400 /home/rektsu/user.txt
fi
unset ZIPPING_USER_FLAG
mkdir -p /run/mysqld /data/mysql /var/www/html/uploads
chown mysql:mysql /run/mysqld /data/mysql
chown www-data:www-data /var/www/html/uploads
if [ ! -d /data/mysql/mysql ]; then
  mariadb-install-db --user=mysql --datadir=/data/mysql --skip-test-db >/dev/null
fi
mariadbd --user=mysql --datadir=/data/mysql --socket=/run/mysqld/mysqld.sock \
  --bind-address=127.0.0.1 --port=3306 --secure-file-priv='' --skip-log-bin >/var/log/zipping-mysql.log 2>&1 &
dbpid=$!
apppid=''
shutdown() {
  if [ -n "$apppid" ]; then kill "$apppid" 2>/dev/null || true; fi
  mariadb-admin --socket=/run/mysqld/mysqld.sock -uroot shutdown >/dev/null 2>&1 || true
  kill "$dbpid" 2>/dev/null || true
  wait "$dbpid" 2>/dev/null || true
  if [ -n "$apppid" ]; then wait "$apppid" 2>/dev/null || true; fi
}
trap shutdown INT TERM EXIT
i=0
until mariadb-admin --socket=/run/mysqld/mysqld.sock -uroot ping >/dev/null 2>&1; do
  i=$((i+1))
  if [ "$i" -ge 60 ] || ! kill -0 "$dbpid" 2>/dev/null; then
    cat /var/log/zipping-mysql.log >&2
    exit 1
  fi
  sleep 1
done
mariadb --socket=/run/mysqld/mysqld.sock -uroot < /opt/zipping/init.sql
apache2ctl -D FOREGROUND &
apppid=$!
wait "$apppid"
