#!/bin/bash
set -euo pipefail
private=$(printenv BASHED_REQUIRE_PRIVATE_FLAGS || true)
user_flag=$(printenv BASHED_STATIC_USER_FLAG || true)
root_flag=$(printenv BASHED_STATIC_ROOT_FLAG || true)
if [ "$private" = 1 ] && { [ -z "$user_flag" ] || [ -z "$root_flag" ]; }; then
  echo "Bashed: private static user/root flags required" >&2
  exit 1
fi
if [ -n "$user_flag" ]; then
  umask 077
  printf '%s\n' "$user_flag" > /home/arrexel/user.txt
  chown arrexel:arrexel /home/arrexel/user.txt
  chmod 0644 /home/arrexel/user.txt
fi
if [ -n "$root_flag" ]; then
  umask 077
  printf '%s\n' "$root_flag" > /root/root.txt
  chown root:root /root/root.txt
  chmod 0600 /root/root.txt
fi
unset private user_flag root_flag BASHED_REQUIRE_PRIVATE_FLAGS BASHED_STATIC_USER_FLAG BASHED_STATIC_ROOT_FLAG
mkdir -p /var/run/apache2
cron -f &
cron_pid=$!
apache2ctl -D FOREGROUND &
apache_pid=$!
wait -n "$cron_pid" "$apache_pid"
status=$?
kill "$cron_pid" "$apache_pid" 2>/dev/null || true
wait 2>/dev/null || true
exit "$status"
