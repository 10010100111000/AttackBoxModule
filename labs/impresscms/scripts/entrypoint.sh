#!/bin/sh
set -eu
mkdir -p /run/mysqld /run/nginx /var/www/trust /var/www/html/uploads /var/www/html/cache /var/www/html/templates_c /var/lib/mysql
chown -R mysql:mysql /run/mysqld /var/lib/mysql
chown -R www-data:www-data /var/www/trust
if [ ! -d /var/lib/mysql/mysql ]; then
    mariadb-install-db --user=mysql --datadir=/var/lib/mysql --skip-test-db >/dev/null
fi
supervisord -n -c /etc/supervisord.conf &
SUPERVISOR_PID=$!
cleanup() {
    kill -TERM "$SUPERVISOR_PID" 2>/dev/null || true
    wait "$SUPERVISOR_PID" 2>/dev/null || true
}
trap cleanup INT TERM
ready=0
for _ in $(seq 1 90); do
    if mariadb-admin --socket=/run/mysqld/mysqld.sock -uroot ping --silent >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 1
done
if [ "$ready" -ne 1 ]; then
    echo "MariaDB did not become ready" >&2
    exit 1
fi
if [ ! -f /var/www/html/mainfile.php ]; then
    DB_PASS="$IMPCMS_DB_PASSWORD"
    if [ -z "$DB_PASS" ]; then
        DB_PASS="$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n')"
    fi
    ADMIN_PASS="${IMPCMS_ADMIN_PASSWORD:-TTP-ImpressCMS-Admin-Only}"
    case "$DB_PASS$ADMIN_PASS" in
        *[!A-Za-z0-9_-]*)
            echo "Database and admin passwords may contain only letters, digits, underscore and hyphen" >&2
            exit 1
            ;;
    esac
    mariadb --socket=/run/mysqld/mysqld.sock -uroot <<SQL
CREATE DATABASE IF NOT EXISTS impresscms CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER IF NOT EXISTS 'impresscms'@'127.0.0.1' IDENTIFIED BY '$DB_PASS';
CREATE USER IF NOT EXISTS 'impresscms'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON impresscms.* TO 'impresscms'@'127.0.0.1';
GRANT ALL PRIVILEGES ON impresscms.* TO 'impresscms'@'localhost';
FLUSH PRIVILEGES;
SQL
    TARGET_IP="${IMPCMS_TARGET_IP:-$(ip -4 -o addr show dev eth0 | awk '{split($4,a,"/"); print a[1]; exit}')}"
    if [ -z "$TARGET_IP" ]; then
        echo "Unable to determine target container IP" >&2
        exit 1
    fi
    TARGET_URL="${IMPCMS_TARGET_URL:-http://$TARGET_IP}"
    chown -R www-data:www-data /var/www/html
    /usr/local/bin/impresscms-install "$TARGET_URL" "$DB_PASS" "$ADMIN_PASS"
    rm -rf /var/www/html/install
    chown -R root:root /var/www/html
    chown -R www-data:www-data /var/www/trust /var/www/html/uploads /var/www/html/cache /var/www/html/templates_c
    chmod -R a+rX /var/www/html
    chmod 0444 /var/www/html/mainfile.php
    chmod 0775 /var/www/html/uploads /var/www/html/cache /var/www/html/templates_c /var/www/trust
    unset DB_PASS ADMIN_PASS
fi
wait "$SUPERVISOR_PID"
