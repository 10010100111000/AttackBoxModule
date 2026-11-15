#!/usr/bin/env bash
set -Eeuo pipefail

# Debian's PostgreSQL package pre-creates a cluster during package installation.
PG_VERSION=15
PG_CLUSTER=main

cleanup() {
  trap - EXIT TERM INT
  for pid in "${ftp_pid:-}" "${ssh_pid:-}"; do
    if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; fi
  done
  pg_ctlcluster "$PG_VERSION" "$PG_CLUSTER" stop -m immediate 2>/dev/null || true
}
trap cleanup EXIT TERM INT

# SSH requires host keys. These are generated at first boot rather than at image build.
ssh-keygen -A >/dev/null

# PostgreSQL must NOT be reachable over the Docker network: SSH tunnel is the goal.
PG_CONF="/etc/postgresql/${PG_VERSION}/${PG_CLUSTER}/postgresql.conf"
sed -i -E "s/^#?listen_addresses\s*=.*/listen_addresses = '127.0.0.1'/" "$PG_CONF"
pg_ctlcluster "$PG_VERSION" "$PG_CLUSTER" start

# Copy the externally-authored flag into the SQL database, rather than storing it
# as a readable file in the unprivileged user's home directory.
if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='christine'" | grep -qx 1; then
  runuser -u postgres -- psql -v ON_ERROR_STOP=1 -c "CREATE ROLE christine LOGIN PASSWORD 'funnel123#!#';"
fi
if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_database WHERE datname='christine'" | grep -qx 1; then
  runuser -u postgres -- createdb -O christine christine
fi
if ! runuser -u postgres -- psql -tAc "SELECT 1 FROM pg_database WHERE datname='secrets'" | grep -qx 1; then
  runuser -u postgres -- createdb -O christine secrets
fi
if ! runuser -u postgres -- psql -d secrets -tAc "SELECT to_regclass('public.flag') IS NOT NULL" | grep -qx t; then
  runuser -u postgres -- psql -d secrets -v ON_ERROR_STOP=1 -c 'CREATE TABLE public.flag (value text NOT NULL); ALTER TABLE public.flag OWNER TO christine;'
fi
if [[ -f /opt/funnel/flag.txt ]]; then
  # Read only from the copied external flag file, then remove the runtime plaintext.
  flag_value="$(cat /opt/funnel/flag.txt)"
  if [[ -z "$flag_value" || "$flag_value" == *$'\n'* ]]; then
    echo 'Flag must be a single nonempty line' >&2; exit 1
  fi
  # PostgreSQL variable substitution via psql --set, avoiding string interpolation in SQL.
  printf "%s\n" "TRUNCATE TABLE public.flag;" "INSERT INTO public.flag (value) VALUES (:'flag_value');" | \
    runuser -u postgres -- psql -d secrets -v ON_ERROR_STOP=1 -v "flag_value=$flag_value"
  rm -f /opt/funnel/flag.txt
fi

/usr/sbin/sshd -D -e & ssh_pid=$!
/usr/sbin/vsftpd /etc/vsftpd.conf & ftp_pid=$!

while kill -0 "$ssh_pid" 2>/dev/null && kill -0 "$ftp_pid" 2>/dev/null; do
  sleep 2
done
echo 'SSH or FTP process stopped' >&2
exit 1
