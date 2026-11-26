#!/bin/sh
set -eu
umask 027
if [ -n "${ALERT_USER_FLAG:-}" ]; then
  su-exec www-data sh -c 'printf "%s\n" "$ALERT_USER_FLAG" > /opt/alert/private/web-flag.txt && chmod 0400 /opt/alert/private/web-flag.txt'
fi
unset ALERT_USER_FLAG
mkdir -p /srv/alert/uploads /srv/alert/messages /run/alert/queue /run/alert/profiles
chown www-data:www-data /srv/alert/uploads
chown www-data:alertbot /srv/alert/messages
chmod 2750 /srv/alert/messages
chown www-data:alertbot /run/alert/queue
chmod 2770 /run/alert/queue
chown alertbot:alertbot /run/alert/profiles
web_pid=''
bot_pid=''
shutdown() {
  [ -z "$web_pid" ] || kill "$web_pid" 2>/dev/null || true
  [ -z "$bot_pid" ] || kill "$bot_pid" 2>/dev/null || true
  [ -z "$web_pid" ] || wait "$web_pid" 2>/dev/null || true
  [ -z "$bot_pid" ] || wait "$bot_pid" 2>/dev/null || true
}
trap shutdown TERM INT EXIT
su-exec www-data php -S 0.0.0.0:8080 -t /srv/alert >/dev/null 2>&1 &
web_pid=$!
su-exec alertbot python3 /opt/alert/bot/review.py &
bot_pid=$!
while kill -0 "$web_pid" 2>/dev/null && kill -0 "$bot_pid" 2>/dev/null; do sleep 1; done
exit 1
