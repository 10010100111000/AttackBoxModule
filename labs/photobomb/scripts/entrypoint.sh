#!/bin/bash
set -euo pipefail
private_flags=$(printenv PHOTOBOMB_REQUIRE_PRIVATE_FLAGS || true)
user_flag=$(printenv PHOTOBOMB_STATIC_USER_FLAG || true)
root_flag=$(printenv PHOTOBOMB_STATIC_ROOT_FLAG || true)
if [ "$private_flags" = "1" ] && { [ -z "$user_flag" ] || [ -z "$root_flag" ]; }; then
  echo "Photobomb: private static user/root flags are required" >&2
  exit 1
fi
if [ -n "$user_flag" ]; then
  umask 077
  printf '%s\n' "$user_flag" > /home/wizard/user.txt
  chown wizard:wizard /home/wizard/user.txt
  chmod 0644 /home/wizard/user.txt
fi
if [ -n "$root_flag" ]; then
  umask 077
  printf '%s\n' "$root_flag" > /root/root.txt
  chown root:root /root/root.txt
  chmod 0600 /root/root.txt
fi
unset private_flags user_flag root_flag PHOTOBOMB_REQUIRE_PRIVATE_FLAGS PHOTOBOMB_STATIC_USER_FLAG PHOTOBOMB_STATIC_ROOT_FLAG
mkdir -p /run/nginx /run/sshd
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -D -e &
sshd_pid=$!
cd /home/wizard/photobomb
su-exec wizard ruby server.rb &
ruby_pid=$!
nginx -g 'daemon off;' &
nginx_pid=$!
wait -n "$sshd_pid" "$ruby_pid" "$nginx_pid"
status=$?
kill "$sshd_pid" "$ruby_pid" "$nginx_pid" 2>/dev/null || true
wait 2>/dev/null || true
exit "$status"
