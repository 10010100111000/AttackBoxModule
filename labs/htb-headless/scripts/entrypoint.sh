#!/bin/sh
set -eu

# Flags are static challenge data baked into this image. The Worker only
# controls the container lifecycle and does not receive or generate Flags.
test -s /home/dvir/user.txt
test -s /root/root.txt

rm -f /tmp/headless-admin-review.ready /tmp/headless-last-reviewed-report
mkdir -p /run/sshd /run/supervisor /home/dvir/app/hacking_reports /tmp/.config /tmp/.cache /tmp/headless-admin-chromium
chown -R dvir:dvir /tmp/.config /tmp/.cache /tmp/headless-admin-chromium
chown -R dvir:dvir /home/dvir/app/hacking_reports
chmod 0700 /home/dvir/app/hacking_reports
ssh-keygen -A

exec /usr/bin/supervisord -n -c /etc/supervisor/supervisord.conf
