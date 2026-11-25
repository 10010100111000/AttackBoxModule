#!/bin/sh
set -eu
FLAG="${INTENSE_WEB_FLAG:-TTP{intense_local_smoke_only}}"
case "$FLAG" in TTP\{*\}) ;; *) echo "INTENSE_WEB_FLAG must use TTP{...} format" >&2; exit 1;; esac
case "$FLAG" in *[!A-Za-z0-9_{}-]* ) echo "INTENSE_WEB_FLAG contains unsupported characters" >&2; exit 1;; esac
mkdir -p /var/lib/intense /app/logs /home/analyst
printf '%s\n' "$FLAG" > /home/analyst/user.txt
chown root:root /home/analyst/user.txt
chmod 0644 /home/analyst/user.txt
unset FLAG INTENSE_WEB_FLAG
export INTENSE_LWT_SECRET_HEX="$(python -c 'import secrets; print(secrets.token_hex(secrets.randbelow(8) + 8))')"
python /app/init_db.py
chown -R web:web /var/lib/intense /app/logs
chmod 0750 /var/lib/intense /app/logs
exec su-exec web:web gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 4 --access-logfile - --error-logfile - --timeout 30 app:app
