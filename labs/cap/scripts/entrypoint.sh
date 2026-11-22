#!/bin/bash
set -euo pipefail
private_flags=$(printenv CAP_REQUIRE_PRIVATE_FLAGS || true)
user_flag=$(printenv CAP_STATIC_USER_FLAG || true)
root_flag=$(printenv CAP_STATIC_ROOT_FLAG || true)
if [ "$private_flags" = "1" ] && { [ -z "$user_flag" ] || [ -z "$root_flag" ]; }; then
  echo "Cap: private static user/root flags are required" >&2
  exit 1
fi
if [ -n "$user_flag" ]; then
  umask 077
  printf '%s\n' "$user_flag" > /home/nathan/user.txt
  chown nathan:nathan /home/nathan/user.txt
  chmod 0400 /home/nathan/user.txt
fi
if [ -n "$root_flag" ]; then
  umask 077
  printf '%s\n' "$root_flag" > /root/root.txt
  chown root:root /root/root.txt
  chmod 0600 /root/root.txt
fi
unset private_flags user_flag root_flag CAP_REQUIRE_PRIVATE_FLAGS CAP_STATIC_USER_FLAG CAP_STATIC_ROOT_FLAG
mkdir -p /run/sshd /var/run/vsftpd/empty
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -D -e &
sshd_pid=$!
/usr/sbin/vsftpd /etc/vsftpd.conf &
ftp_pid=$!
su-exec nathan /usr/bin/python3.8 /app/app.py &
web_pid=$!
wait -n "$sshd_pid" "$ftp_pid" "$web_pid"
status=$?
kill "$sshd_pid" "$ftp_pid" "$web_pid" 2>/dev/null || true
wait 2>/dev/null || true
exit "$status"
