#!/bin/sh
set -eu
mkdir -p /run/postgresql /var/lib/postgresql/data
chown -R postgres:postgres /run/postgresql /var/lib/postgresql
if [ ! -s /var/lib/postgresql/data/PG_VERSION ]; then
  su-exec postgres initdb -D /var/lib/postgresql/data --auth-local=trust --auth-host=trust >/dev/null
fi
su-exec postgres pg_ctl -D /var/lib/postgresql/data -o "-h 127.0.0.1 -k /run/postgresql" -w start >/dev/null
su-exec postgres psql -h 127.0.0.1 -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='lab'" | grep -q 1 || su-exec postgres createdb -h 127.0.0.1 -U postgres lab
python /app/app.py migrate --noinput
# Do not use public/host network. Worker maps this service only into the lab network.
exec su-exec lab python /app/app.py runserver 0.0.0.0:8000 --noreload
