#!/bin/bash
set -euo pipefail

user_flag=$(printenv BOUNTYHUNTER_STATIC_USER_FLAG || true)
root_flag=$(printenv BOUNTYHUNTER_STATIC_ROOT_FLAG || true)
required=$(printenv BOUNTYHUNTER_REQUIRE_PRIVATE_FLAGS || true)
if [ "$required" = 1 ] && { [ -z "$user_flag" ] || [ -z "$root_flag" ]; }; then
  echo 'BountyHunter: both private flags are required' >&2
  exit 1
fi
if [ -n "$user_flag" ]; then
  umask 077
  printf '%s\n' "$user_flag" > /home/development/user.txt
fi
if [ -n "$root_flag" ]; then
  umask 077
  printf '%s\n' "$root_flag" > /root/root.txt
fi
chown development:development /home/development/user.txt
chmod 0640 /home/development/user.txt
chown root:root /root/root.txt
chmod 0600 /root/root.txt
unset user_flag root_flag required
unset BOUNTYHUNTER_STATIC_USER_FLAG BOUNTYHUNTER_STATIC_ROOT_FLAG BOUNTYHUNTER_REQUIRE_PRIVATE_FLAGS
# Restore the normal process umask after protected flags are initialized.
umask 022

mkdir -p /run/apache2 /run/php /run/sshd
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -D -e &
ssh_pid=$!
php-fpm83 -F &
php_pid=$!
httpd -DFOREGROUND &
http_pid=$!
cleanup() {
  kill "$http_pid" "$php_pid" "$ssh_pid" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT
wait -n "$http_pid" "$php_pid" "$ssh_pid"
echo "BountyHunter: a required service terminated" >&2
exit 1
