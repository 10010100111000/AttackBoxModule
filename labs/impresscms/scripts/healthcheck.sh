#!/bin/sh
set -eu
curl -fsS --max-time 4 http://127.0.0.1/ >/dev/null
php /usr/local/bin/impresscms-db-health.php
