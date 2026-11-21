#!/usr/bin/env bash
set -euo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
port=18095
php -l "$here/public/index.php" >/dev/null
php -S "127.0.0.1:$port" -t "$here/public" "$here/tests/router.php" >"$here/php-smoke.log" 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; rm -f "$here/php-smoke.log"' EXIT
for _ in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:$port/" >/dev/null 2>&1; then break; fi
  sleep 0.1
done
page=$(curl -fsS "http://127.0.0.1:$port/")
grep -qF '<title>Pebbles</title>' <<<"$page"
grep -qF 'name="username"' <<<"$page"
grep -qF 'name="password"' <<<"$page"
if grep -qi 'ZoneMinder' <<<"$page"; then echo 'ZoneMinder clue leaked' >&2; exit 1; fi
post=$(curl -fsS -d 'username=admin&password=admin' "http://127.0.0.1:$port/")
grep -qF 'Invalid username or password' <<<"$post"
status=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$port/zm/")
test "$status" = 404
echo 'PASS: PHP entry page does not reveal ZoneMinder'
