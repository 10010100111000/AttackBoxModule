#!/bin/bash
set -euo pipefail
curl -fsS --max-time 4 http://127.0.0.1/ | grep -Fq 'Bashed'
curl -fsS --max-time 4 http://127.0.0.1/dev/phpbash.php | grep -Fq 'phpbash'
pidof cron >/dev/null
