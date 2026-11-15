#!/bin/bash
set -Eeuo pipefail
export DEBIAN_FRONTEND=noninteractive
DB_USER='lewis'
DB_PASS='P4ntherg0t1n5r3c0n##'
DB_NAME='joomla'
WEBROOT='/var/www/dev.devvortex.htb'

mkdir -p /run/mysqld /run/php /run/sshd
chown mysql:mysql /run/mysqld
if [[ ! -d /var/lib/mysql/mysql ]]; then
    mariadb-install-db --user=mysql --datadir=/var/lib/mysql >/dev/null
fi
mariadbd --user=mysql --bind-address=127.0.0.1 --socket=/run/mysqld/mysqld.sock &
MYSQL_PID=$!
for _ in $(seq 1 60); do
    if mariadb-admin ping --silent >/dev/null 2>&1; then break; fi
    sleep 1
done
mariadb-admin ping --silent >/dev/null || { echo 'MariaDB failed to start' >&2; exit 1; }
mariadb --protocol=socket -uroot <<SQL
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
ALTER USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
SQL

if [[ ! -f "$WEBROOT/configuration.php" ]]; then
    echo 'Initializing Joomla 4.2.6 (first startup)...'
    cd "$WEBROOT"
    # Installer has to be run as the web server user for subsequent template edits.
    su -s /bin/sh www-data -c "php installation/joomla.php install \
      --site-name='Devvortex' \
      --admin-user='Lewis' \
      --admin-username='lewis' \
      --admin-password='$DB_PASS' \
      --admin-email='lewis@devvortex.htb' \
      --db-type='mysqli' \
      --db-host='localhost' \
      --db-user='$DB_USER' \
      --db-pass='$DB_PASS' \
      --db-name='$DB_NAME' \
      --db-prefix='sd4fg_' \
      --db-encryption=0 \
      --no-interaction"
    [[ -f "$WEBROOT/configuration.php" ]] || { echo 'Joomla installation failed' >&2; exit 1; }
fi

# Insert the second user into the real Joomla users table. This stores a real bcrypt hash.
HASH=$(php -r 'echo password_hash("tequieromucho", PASSWORD_BCRYPT);')
mariadb --protocol=socket -uroot "$DB_NAME" <<SQL
INSERT INTO sd4fg_users (name,username,email,password,block,sendEmail,registerDate,params)
SELECT 'Logan','logan','logan@devvortex.htb','$HASH',0,0,NOW(),'{}'
WHERE NOT EXISTS (SELECT 1 FROM sd4fg_users WHERE username='logan');
SQL
chown -R www-data:www-data "$WEBROOT"
chmod 640 "$WEBROOT/configuration.php"
ssh-keygen -A >/dev/null
php-fpm8.1 -D
nginx
/usr/sbin/sshd

echo 'Devvortex: nginx, Joomla/PHP, MariaDB and SSH are running.'
# Bash PID 1 remains as supervisor and exits if a required daemon fails.
trap 'kill "$MYSQL_PID" 2>/dev/null || true; service nginx stop >/dev/null 2>&1 || true; service php8.1-fpm stop >/dev/null 2>&1 || true; pkill sshd || true' TERM INT
while true; do
    kill -0 "$MYSQL_PID" 2>/dev/null || { echo 'MariaDB exited' >&2; exit 1; }
    pgrep -x nginx >/dev/null || { echo 'Nginx exited' >&2; exit 1; }
    pgrep -x php-fpm8.1 >/dev/null || { echo 'PHP-FPM exited' >&2; exit 1; }
    pgrep -x sshd >/dev/null || { echo 'SSHD exited' >&2; exit 1; }
    sleep 5 & wait $!
done
