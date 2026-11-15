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
CREATE USER IF NOT EXISTS '$DB_USER'@'127.0.0.1' IDENTIFIED BY '$DB_PASS';
ALTER USER '$DB_USER'@'127.0.0.1' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'127.0.0.1';
FLUSH PRIVILEGES;
SQL

if [[ ! -f "$WEBROOT/configuration.php" ]]; then
    echo 'Initializing Joomla 4.2.6 database and configuration...'
    sed "s/#__/sd4fg_/g" "$WEBROOT/installation/sql/mysql/base.sql" | mariadb --protocol=socket -uroot "$DB_NAME"
    sed "s/#__/sd4fg_/g" "$WEBROOT/installation/sql/mysql/supports.sql" | mariadb --protocol=socket -uroot "$DB_NAME"
    sed "s/#__/sd4fg_/g" "$WEBROOT/installation/sql/mysql/extensions.sql" | mariadb --protocol=socket -uroot "$DB_NAME"

    LEWIS_HASH=$(php -r 'echo password_hash("P4ntherg0t1n5r3c0n##", PASSWORD_BCRYPT);')
    LOGAN_HASH=$(php -r 'echo password_hash("tequieromucho", PASSWORD_BCRYPT);')

    mariadb --protocol=socket -uroot "$DB_NAME" <<SQL
INSERT INTO sd4fg_users (id, name, username, email, password, block, sendEmail, registerDate, lastvisitDate, activation, params)
VALUES
(1, 'Lewis', 'lewis', 'lewis@devvortex.htb', '$LEWIS_HASH', 0, 1, NOW(), '0000-00-00 00:00:00', '', '{}'),
(2, 'Logan', 'logan', 'logan@devvortex.htb', '$LOGAN_HASH', 0, 0, NOW(), '0000-00-00 00:00:00', '', '{}');
INSERT INTO sd4fg_user_usergroup_map (user_id, group_id) VALUES (1, 8), (2, 2);
SQL

    cat << "CONFIG" > "$WEBROOT/configuration.php"
<?php
class JConfig
{
	public $offline = false;
	public $offline_message = 'This site is down for maintenance.<br> Please check back again soon.';
	public $display_offline_message = 1;
	public $offline_image = '';
	public $sitename = 'Devvortex';
	public $editor = 'tinymce';
	public $captcha = 0;
	public $list_limit = 20;
	public $access = 1;
	public $frontediting = 1;
	public $dbtype = 'mysqli';
	public $host = 'localhost';
	public $user = 'lewis';
	public $password = 'P4ntherg0t1n5r3c0n##';
	public $db = 'joomla';
	public $dbprefix = 'sd4fg_';
	public $dbencryption = 0;
	public $dbsslverifyservercert = false;
	public $secret = 'k3Y9wZ1vB2c8X7m4L5p0Q6r1S2t3U4v5';
	public $gzip = false;
	public $error_reporting = 'default';
	public $tmp_path = '/var/www/dev.devvortex.htb/tmp';
	public $log_path = '/var/www/dev.devvortex.htb/administrator/logs';
	public $live_site = '';
	public $force_ssl = 0;
	public $offset = 'UTC';
	public $lifetime = 15;
	public $session_handler = 'database';
	public $shared_session = false;
	public $session_metadata = true;
	public $mailonline = true;
	public $mailer = 'mail';
	public $mailfrom = 'lewis@devvortex.htb';
	public $fromname = 'Devvortex';
	public $caching = 0;
	public $cachetime = 15;
	public $cache_handler = 'file';
	public $cors = false;
	public $cors_allow_origin = '*';
	public $debug = false;
	public $sef = true;
	public $asset_id = 1;
}
CONFIG

    rm -rf "$WEBROOT/installation"
    chown -R www-data:www-data "$WEBROOT"
    chmod 640 "$WEBROOT/configuration.php"
fi

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
