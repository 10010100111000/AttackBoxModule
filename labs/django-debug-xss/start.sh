#!/bin/sh
set -eu
mkdir -p /run/postgresql /var/lib/postgresql/data
chown -R postgres:postgres /run/postgresql /var/lib/postgresql
if [ ! -s /var/lib/postgresql/data/PG_VERSION ]; then
  su-exec postgres initdb -D /var/lib/postgresql/data --auth-local=trust --auth-host=trust >/dev/null
fi
su-exec postgres pg_ctl -D /var/lib/postgresql/data -o "-h 127.0.0.1 -k /run/postgresql" -w start >/dev/null
su-exec postgres psql -h 127.0.0.1 -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='lab'" | grep -q 1 || su-exec postgres createdb -h 127.0.0.1 -U postgres lab
mkdir -p /run/django/reports /run/django/bot-state/profiles
chown lab:reviewbot /run/django/reports
chmod 2770 /run/django/reports
chown -R reviewbot:reviewbot /run/django/bot-state
chmod 0700 /run/django/bot-state/profiles
python /usr/local/bin/seed-lab.py
unset DJANGO_EDITOR_PASSWORD DJANGO_XSS_FLAG
python /app/app.py migrate --noinput
# Do not use public/host network. Worker maps this service only into the lab network.
su-exec reviewbot python /opt/review/bot.py &
bot_pid=$!
su-exec lab python /app/app.py runserver 0.0.0.0:8000 --noreload &
web_pid=$!
cleanup() {
  kill "$bot_pid" "$web_pid" 2>/dev/null || true
  wait "$bot_pid" "$web_pid" 2>/dev/null || true
  su-exec postgres pg_ctl -D /var/lib/postgresql/data -m immediate stop >/dev/null 2>&1 || true
}
trap cleanup INT TERM
while kill -0 "$bot_pid" 2>/dev/null && kill -0 "$web_pid" 2>/dev/null; do sleep 1; done
cleanup
exit 1
