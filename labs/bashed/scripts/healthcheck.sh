#!/bin/bash
set -euo pipefail
curl -fsS --max-time 4 http://127.0.0.1/ | grep -F 'Bashed' >/dev/null
curl -fsS --max-time 4 http://127.0.0.1/dev/phpbash.php | grep -F 'phpbash' >/dev/null
pidof cron >/dev/null
