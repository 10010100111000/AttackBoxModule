#!/bin/sh
set -eu
BASE_URL="${BASE_URL:-http://127.0.0.1:8080}"
ADMIN_HOST="${ADMIN_HOST:-internal-administration.goodgames.htb}"

printf '[1/5] health endpoint... '
curl -fsS "$BASE_URL/healthz" | grep -q '"status":"ok"'
echo OK

printf '[2/5] Game Warrior homepage... '
curl -fsS "$BASE_URL/" | grep -q 'loginModal'
echo OK

printf '[3/5] Game Warrior assets... '
curl -fsS "$BASE_URL/css/style.css" | grep -q 'body'
echo OK

printf '[4/5] admin Volt login page... '
curl -fsS -H "Host: $ADMIN_HOST" "$BASE_URL/login" | grep -q 'GoodGames internal administration'
echo OK

printf '[5/5] admin login and settings... '
COOKIE_JAR="$(mktemp)"
trap 'rm -f "$COOKIE_JAR"' EXIT
curl -fsS -c "$COOKIE_JAR" -b "$COOKIE_JAR" -H "Host: $ADMIN_HOST" -d 'username=admin&password=superadministrator' "$BASE_URL/login" -o /dev/null
curl -fsS -c "$COOKIE_JAR" -b "$COOKIE_JAR" -H "Host: $ADMIN_HOST" "$BASE_URL/settings" | grep -q 'User Settings'
echo OK

echo 'All smoke tests passed.'
