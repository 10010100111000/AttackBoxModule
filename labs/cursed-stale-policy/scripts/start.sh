#!/bin/sh
set -eu

if [ -n "${CSP_ADMIN_FLAG:-}" ]; then
  chmod 0644 /flag.txt
  printf '%s\n' "$CSP_ADMIN_FLAG" > /flag.txt
  chmod 0444 /flag.txt
fi
unset CSP_ADMIN_FLAG

exec /usr/bin/supervisord -c /etc/supervisord.conf
