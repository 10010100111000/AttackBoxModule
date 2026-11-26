#!/bin/sh
set -eu

: "\${HEADLESS_USER_FLAG:?HEADLESS_USER_FLAG must be supplied by the Worker}"
: "\${HEADLESS_ROOT_FLAG:?HEADLESS_ROOT_FLAG must be supplied by the Worker}"

printf '%s\n' "$HEADLESS_USER_FLAG" > /home/dvir/user.txt
printf '%s\n' "$HEADLESS_ROOT_FLAG" > /root/root.txt
chown dvir:dvir /home/dvir/user.txt
chown root:root /root/root.txt
chmod 0400 /home/dvir/user.txt
chmod 0600 /root/root.txt

rm -f /tmp/headless-admin-review.ready
mkdir -p /run/sshd /run/supervisor /home/dvir/app/hacking_reports /tmp/.config /tmp/.cache /tmp/headless-admin-chromium
chown -R dvir:dvir /tmp/.config /tmp/.cache /tmp/headless-admin-chromium
chown -R dvir:dvir /home/dvir/app/hacking_reports
chmod 0700 /home/dvir/app/hacking_reports
ssh-keygen -A

exec /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
