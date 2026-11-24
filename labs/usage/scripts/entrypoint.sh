#!/bin/bash
set -euo pipefail

if [[ "${USAGE_REQUIRE_PRIVATE_FLAGS:-1}" == "1" ]]; then
  : "${USAGE_STATIC_USER_FLAG:?Worker must inject USAGE_STATIC_USER_FLAG}"
  : "${USAGE_STATIC_ROOT_FLAG:?Worker must inject USAGE_STATIC_ROOT_FLAG}"
fi
USER_FLAG="${USAGE_STATIC_USER_FLAG:-TTP{usage_demo_user_only}}"
ROOT_FLAG="${USAGE_STATIC_ROOT_FLAG:-TTP{usage_demo_root_only}}"
[[ "$USER_FLAG" != "$ROOT_FLAG" ]] || { echo "User and Root flags must differ" >&2; exit 1; }
# Keep instance answers out of all child-process environments.
unset USAGE_STATIC_USER_FLAG USAGE_STATIC_ROOT_FLAG

install -d -o mysql -g mysql -m 0750 /var/lib/mysql /var/run/mysqld
install -d -o root -g root -m 0755 /run/usage /var/backups
install -d -o dash -g xander -m 2775 /var/www/usage/public/uploads/images
install -d -o dash -g xander -m 0775 /var/www/usage/storage /var/www/usage/bootstrap/cache
install -d -o dash -g dash -m 0700 /home/dash/.ssh
chown -R dash:dash /home/dash
chmod 0750 /home/dash
# With UsePAM=no, OpenSSH rejects a locked shadow account even for keys.
# Set an independent high-entropy password; SSH permits only public keys for dash.
printf 'dash:%s\n' "$(openssl rand -hex 32)" | chpasswd

if [[ ! -d /var/lib/mysql/mysql ]]; then
  echo "[usage] Initializing genuine MySQL 8.0 datadir"
  mysqld --initialize-insecure --user=mysql --datadir=/var/lib/mysql
fi

MYSQL_SOCKET=/var/lib/mysql/mysql.sock
mysqld --user=mysql --datadir=/var/lib/mysql --socket="$MYSQL_SOCKET" \
  --pid-file=/var/run/mysqld/mysqld.pid --bind-address=127.0.0.1 \
  --innodb-buffer-pool-size=96M --performance-schema=OFF \
  --mysqlx=OFF --mysqlx-bind-address=127.0.0.1 &
MYSQL_PID=$!

for i in $(seq 1 90); do
  if mysqladmin --protocol=socket --socket="$MYSQL_SOCKET" -uroot ping --silent >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$MYSQL_PID" 2>/dev/null; then
    echo "[usage] MySQL exited during startup" >&2
    wait "$MYSQL_PID" || true
    exit 1
  fi
  sleep 1
done
mysqladmin --protocol=socket --socket="$MYSQL_SOCKET" -uroot ping --silent >/dev/null

if [[ ! -s /var/lib/mysql/.usage-root-password ]]; then
  MYSQL_ROOT_PASSWORD="$(openssl rand -hex 20)"
  mysql --protocol=socket --socket="$MYSQL_SOCKET" -uroot -e \
    "ALTER USER 'root'@'localhost' IDENTIFIED BY '$MYSQL_ROOT_PASSWORD';"
  printf '%s' "$MYSQL_ROOT_PASSWORD" > /var/lib/mysql/.usage-root-password
  chmod 0600 /var/lib/mysql/.usage-root-password
  chown mysql:mysql /var/lib/mysql/.usage-root-password
else
  MYSQL_ROOT_PASSWORD="$(cat /var/lib/mysql/.usage-root-password)"
fi

if [[ ! -s /var/lib/mysql/.usage-app-password ]]; then
  MYSQL_APP_PASSWORD="$(openssl rand -hex 20)"
  printf '%s' "$MYSQL_APP_PASSWORD" > /var/lib/mysql/.usage-app-password
  chmod 0600 /var/lib/mysql/.usage-app-password
  chown mysql:mysql /var/lib/mysql/.usage-app-password
else
  MYSQL_APP_PASSWORD="$(cat /var/lib/mysql/.usage-app-password)"
fi

mysql --protocol=socket --socket="$MYSQL_SOCKET" -uroot -p"$MYSQL_ROOT_PASSWORD" <<SQL
CREATE DATABASE IF NOT EXISTS usage_blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'usage_app'@'127.0.0.1' IDENTIFIED BY '$MYSQL_APP_PASSWORD';
ALTER USER 'usage_app'@'127.0.0.1' IDENTIFIED BY '$MYSQL_APP_PASSWORD';
GRANT ALL PRIVILEGES ON usage_blog.* TO 'usage_app'@'127.0.0.1';
FLUSH PRIVILEGES;
SQL

if [[ ! -f /var/www/usage/.env ]]; then
  cp /var/www/usage/.env.example /var/www/usage/.env
fi
cat > /var/www/usage/.env <<ENV
APP_NAME=DailyBlogs
APP_ENV=production
APP_KEY=
APP_DEBUG=false
APP_URL=http://usage.htb
LOG_CHANNEL=stderr
LOG_LEVEL=warning
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=usage_blog
DB_USERNAME=usage_app
DB_PASSWORD=$MYSQL_APP_PASSWORD
BROADCAST_DRIVER=log
CACHE_DRIVER=file
FILESYSTEM_DISK=local
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120
ADMIN_ROUTE_PREFIX=
ENV
chown root:dash /var/www/usage/.env
chmod 0640 /var/www/usage/.env
cd /var/www/usage
php artisan key:generate --force --no-interaction
php artisan config:clear
APP_ENV=local php artisan admin:install --no-interaction
php artisan db:seed --class=Database\\Seeders\\UsageSeeder --force --no-interaction
php artisan config:cache
php artisan route:cache
php artisan view:cache

# Per-instance system credentials: the Monit password is intentionally reused
# by xander and is discoverable from dash's real .monitrc after the foothold.
MONIT_PASSWORD="$(openssl rand -hex 8)"
printf 'xander:%s\n' "$MONIT_PASSWORD" | chpasswd
cat > /home/dash/.monitrc <<MONIT
set daemon 60
set pidfile /home/dash/.monit.pid
set statefile /home/dash/.monit.state
set logfile /home/dash/.monit.log
set httpd port 2812
    use address 127.0.0.1
    allow admin:$MONIT_PASSWORD
check system usage
    if memory usage > 85% for 2 cycles then alert
    if cpu usage (user) > 85% for 2 cycles then alert
check filesystem rootfs with path /
    if space usage > 85% then alert
MONIT
chown dash:dash /home/dash/.monitrc
chmod 0700 /home/dash/.monitrc

if [[ ! -s /home/dash/.ssh/id_rsa ]]; then
  ssh-keygen -q -t rsa -b 2048 -N '' -f /home/dash/.ssh/id_rsa
  cp /home/dash/.ssh/id_rsa.pub /home/dash/.ssh/authorized_keys
fi
chown -R dash:dash /home/dash/.ssh
chmod 0700 /home/dash/.ssh
chmod 0600 /home/dash/.ssh/id_rsa /home/dash/.ssh/authorized_keys
ssh-keygen -A
mkdir -p /run/sshd
chmod 0755 /run/sshd

printf '%s\n' "$USER_FLAG" > /home/dash/user.txt
chown root:dash /home/dash/user.txt
chmod 0640 /home/dash/user.txt
printf '%s\n' "$ROOT_FLAG" > /root/root.txt
chown root:root /root/root.txt
chmod 0600 /root/root.txt
unset USER_FLAG ROOT_FLAG

# The real p7zip 16.02 binary is invoked directly through sudo. No helper
# binary or fake privilege-escalation result is inserted into the chain.
chown root:xander /var/www/usage/public
chmod 0775 /var/www/usage/public
visudo -cf /etc/sudoers >/dev/null

php-fpm --test
nginx -t
sshd -t

su -s /bin/bash dash -c 'monit -c /home/dash/.monitrc' || true
/usr/sbin/sshd -E /var/log/usage-sshd.log
php-fpm -F &
PHP_PID=$!
nginx -g 'daemon off;' &
NGINX_PID=$!

cleanup() {
  kill "$PHP_PID" "$NGINX_PID" "$MYSQL_PID" 2>/dev/null || true
  wait "$PHP_PID" "$NGINX_PID" "$MYSQL_PID" 2>/dev/null || true
  su -s /bin/bash dash -c 'monit -c /home/dash/.monitrc quit' >/dev/null 2>&1 || true
}
trap cleanup INT TERM EXIT

echo "[usage] MySQL $(mysql --version | awk '{print $5}') ready; Laravel Usage app and admin vhost starting"
while kill -0 "$PHP_PID" 2>/dev/null && kill -0 "$NGINX_PID" 2>/dev/null && kill -0 "$MYSQL_PID" 2>/dev/null; do
  sleep 2
done
echo "[usage] A supervised service exited" >&2
exit 1
