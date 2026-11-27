#!/bin/sh
set -eu
require=$(printenv SHOCKER_REQUIRE_PRIVATE_FLAGS || true)
user_flag=$(printenv SHOCKER_STATIC_USER_FLAG || true)
root_flag=$(printenv SHOCKER_STATIC_ROOT_FLAG || true)
if [ "$require" = 1 ] && { [ -z "$user_flag" ] || [ -z "$root_flag" ]; }; then
  echo "Shocker: private static user and root flags required" >&2
  exit 1
fi
if [ -n "$user_flag" ]; then
  umask 077
  printf '%s\n' "$user_flag" > /home/shelly/user.txt
  chown shelly:shelly /home/shelly/user.txt
  chmod 0644 /home/shelly/user.txt
fi
if [ -n "$root_flag" ]; then
  umask 077
  printf '%s\n' "$root_flag" > /root/root.txt
  chown root:root /root/root.txt
  chmod 0600 /root/root.txt
fi
unset user_flag root_flag require SHOCKER_STATIC_USER_FLAG SHOCKER_STATIC_ROOT_FLAG SHOCKER_REQUIRE_PRIVATE_FLAGS
mkdir -p /run/apache2 /run/sshd
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -e
exec /usr/sbin/httpd -DFOREGROUND
