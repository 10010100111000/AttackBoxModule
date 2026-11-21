#!/usr/bin/env bash
# Real multi-service stack for an intentionally vulnerable isolated Docker lab.
set -Eeuo pipefail

mysql_pid=""
apache_pid=""
ftp_pid=""
ssh_pid=""
tomcat_pid=""
say() { printf '[pebbles] %s\n' "$*" >&2; }
shutdown() {
    trap - TERM INT EXIT
    say 'stopping lab services'
    /usr/bin/zmpkg.pl stop >/dev/null 2>&1 || true
    for pid in "$tomcat_pid" "$apache_pid" "$ssh_pid" "$ftp_pid" "$mysql_pid"; do
        if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; fi
    done
    for pid in "$tomcat_pid" "$apache_pid" "$ssh_pid" "$ftp_pid" "$mysql_pid"; do
        if [[ -n "$pid" ]]; then wait "$pid" 2>/dev/null || true; fi
    done
}
trap shutdown EXIT
trap 'exit 143' TERM INT

# Production uses a fixed static answer supplied through Worker environment variables.
# Never put the real answer in this public Docker image.
if [[ "${PEBBLES_REQUIRE_STATIC_FLAG:-0}" == 1 && -z "${PEBBLES_STATIC_ROOT_FLAG:-}" ]]; then
    say 'private static Flag required; refusing to use the public demo'
    exit 1
fi
if [[ -n "${PEBBLES_STATIC_ROOT_FLAG:-}" ]]; then
    root_flag="$PEBBLES_STATIC_ROOT_FLAG"
    if [[ ${#root_flag} -lt 16 || ${#root_flag} -gt 128 ]] || [[ "$root_flag" =~ [[:cntrl:]] ]]; then
        say 'invalid static Flag: must be 16-128 printable characters'
        exit 1
    fi
    (umask 077; printf '%s\n' "$root_flag" > /root/proof.txt)
    chmod 0600 /root/proof.txt
    unset root_flag PEBBLES_STATIC_ROOT_FLAG
fi
unset PEBBLES_REQUIRE_STATIC_FLAG
mkdir -p /run/mysqld /run/sshd /run/zm /var/log/mysql /var/log/zoneminder
# /run is ephemeral in Docker; vsftpd needs an empty, non-writable chroot.
install -d -o root -g root -m 0555 /var/run/vsftpd/empty
chown root:root /run/mysqld /var/log/mysql
chown -R www-data:www-data /run/zm /var/log/zoneminder

# This unsafe original-machine setting is confined to the Docker container.
/usr/sbin/mysqld --user=root \
    --datadir=/var/lib/mysql --socket=/run/mysqld/mysqld.sock \
    --pid-file=/run/mysqld/mysqld.pid --bind-address=127.0.0.1 \
    --port=3306 --secure-file-priv='' --sql-mode=NO_ENGINE_SUBSTITUTION \
    --log-error=/var/log/mysql/pebbles-error.log &
mysql_pid=$!
ready=0
for i in $(seq 1 120); do
    if ! kill -0 "$mysql_pid" 2>/dev/null; then
        say 'MySQL exited during startup'; tail -100 /var/log/mysql/pebbles-error.log >&2 || true; exit 1
    fi
    if mysqladmin --protocol=socket --socket=/run/mysqld/mysqld.sock ping >/dev/null 2>&1; then
        ready=1; break
    fi
    sleep 1
done
if [[ "$ready" != 1 ]]; then
    say 'MySQL startup timed out'; tail -100 /var/log/mysql/pebbles-error.log >&2 || true; exit 1
fi

mysql_root=( mysql --protocol=socket --socket=/run/mysqld/mysqld.sock --user=root --password="${PEBBLES_MYSQL_BOOTSTRAP:-pebbles-bootstrap-only}" )
if ! "${mysql_root[@]}" -Nse 'SELECT 1' >/dev/null 2>&1; then
    mysql_root=( mysql --protocol=socket --socket=/run/mysqld/mysqld.sock --user=root )
    if ! "${mysql_root[@]}" -Nse 'SELECT 1' >/dev/null 2>&1; then
        say 'Cannot authenticate as historical MySQL root'; exit 1
    fi
fi

# Import the actual upstream schema rather than creating a lookalike database.
if ! "${mysql_root[@]}" -Nse "SHOW DATABASES LIKE 'zm'" | grep -Fxq zm; then
    say 'initializing genuine ZoneMinder schema'
    "${mysql_root[@]}" < /usr/share/zoneminder/db/zm_create.sql
fi
# Original deliberately dangerous DBA permission grants for the vulnerable app.
"${mysql_root[@]}" -e "GRANT ALL PRIVILEGES ON *.* TO 'zmuser'@'localhost' IDENTIFIED BY 'zmpass' WITH GRANT OPTION; FLUSH PRIVILEGES;"
if ! mysql --protocol=socket --user=zmuser --password=zmpass -D zm -Nse 'SELECT COUNT(*) FROM Logs' >/dev/null 2>&1; then
    say 'Genuine ZoneMinder database login did not work'; exit 1
fi

sed -ri 's|^ZM_DB_HOST=.*|ZM_DB_HOST=localhost|; s|^ZM_DB_NAME=.*|ZM_DB_NAME=zm|; s|^ZM_DB_USER=.*|ZM_DB_USER=zmuser|; s|^ZM_DB_PASS=.*|ZM_DB_PASS=zmpass|' /etc/zm/zm.conf
chown root:www-data /etc/zm/zm.conf
chmod 0640 /etc/zm/zm.conf
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -D -e &
ssh_pid=$!
/usr/sbin/vsftpd /etc/vsftpd.conf &
ftp_pid=$!

/usr/sbin/apache2ctl -D FOREGROUND &
apache_pid=$!
su -s /bin/sh -c 'exec /opt/tomcat/bin/catalina.sh run' tomcat &
tomcat_pid=$!

say 'starting original ZoneMinder daemons'
if ! /usr/bin/zmpkg.pl start; then
    say 'original ZoneMinder daemon failed to start'; exit 1
fi

for i in $(seq 1 90); do
    if /usr/local/bin/pebbles-healthcheck >/dev/null 2>&1; then
        say 'original ports and services ready'; break
    fi
    for pid in "$mysql_pid" "$apache_pid" "$ftp_pid" "$ssh_pid" "$tomcat_pid"; do
        if ! kill -0 "$pid" 2>/dev/null; then
            say "service process $pid exited during initialization"; exit 1
        fi
    done
    if [[ "$i" == 90 ]]; then say 'health checks never passed'; exit 1; fi
    sleep 2
done

while true; do
    for pid in "$mysql_pid" "$apache_pid" "$ftp_pid" "$ssh_pid" "$tomcat_pid"; do
        if ! kill -0 "$pid" 2>/dev/null; then say "service process $pid exited"; exit 1; fi
    done
    sleep 5
done
