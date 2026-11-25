#!/bin/sh
set -eu
TARGET_URL="$1"
DB_PASS="$2"
ADMIN_PASS="$3"
COOKIE=/tmp/impresscms-installer.cookies
BASE=http://127.0.0.1
ROOT=/var/www/html
TRUST=/var/www/trust

request_get() {
    curl -fsS -c "$COOKIE" -b "$COOKIE" "$BASE/install/$1" -o /dev/null
}
request_post() {
    page="$1"
    shift
    curl -sS -c "$COOKIE" -b "$COOKIE" -o /tmp/impresscms-installer-response \
        -X POST "$@" "$BASE/install/$page"
}

request_get page_langselect.php
request_post page_langselect.php --data-urlencode "lang=english"

request_get page_pathsettings.php
request_post page_pathsettings.php \
    --data-urlencode "URL=$TARGET_URL" \
    --data-urlencode "ROOT_PATH=$ROOT" \
    --data-urlencode "TRUST_PATH=$TRUST"

request_get page_dbconnection.php
request_post page_dbconnection.php \
    --data-urlencode "DB_TYPE=pdo.mysql" \
    --data-urlencode "DB_HOST=127.0.0.1" \
    --data-urlencode "DB_USER=impresscms" \
    --data-urlencode "DB_PASS=$DB_PASS"

request_get page_dbsettings.php
request_post page_dbsettings.php \
    --data-urlencode "DB_NAME=impresscms" \
    --data-urlencode "DB_CHARSET=utf8" \
    --data-urlencode "DB_COLLATION=utf8_general_ci" \
    --data-urlencode "DB_PREFIX=icms" \
    --data-urlencode "DB_SALT=$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n')"

request_get page_configsave.php
request_post page_configsave.php
request_get page_tablescreate.php
request_post page_tablescreate.php
request_get page_siteinit.php
request_post page_siteinit.php \
    --data-urlencode "adminname=Administrator" \
    --data-urlencode "adminlogin_name=admin" \
    --data-urlencode "adminmail=admin@impresscms.local" \
    --data-urlencode "adminpass=$ADMIN_PASS" \
    --data-urlencode "adminpass2=$ADMIN_PASS"
request_get page_tablesfill.php
request_post page_tablesfill.php
request_get page_modulesinstall.php
request_post page_modulesinstall.php \
    --data-urlencode "mod=1" \
    --data-urlencode "install_mods[]=content"

curl -fsS -c "$COOKIE" -b "$COOKIE" "$BASE/install/page_end.php?success=1" -o /dev/null
if [ ! -f "$ROOT/mainfile.php" ] || [ -d "$ROOT/install" ]; then
    echo "ImpressCMS installer did not finish cleanly" >&2
    exit 1
fi
echo "ImpressCMS installer completed"
