#!/bin/sh
set -eu
umask 027

# Seed the genuine WonderCMS database and instance-only bot credentials/Flag.
php /usr/local/bin/wcms-seed.php

mkdir -p /run/wcms/reports /run/wcms/bot-state/profiles
chown www-data:wcmsbot /run/wcms/reports
chmod 2770 /run/wcms/reports
chown -R wcmsbot:wcmsbot /run/wcms/bot-state
chmod 0750 /run/wcms/bot-state; chmod 0700 /run/wcms/bot-state/profiles

# Do not leave plaintext bootstrap credentials in the web process environment.
unset WONDERCMS_ADMIN_PASSWORD WONDERCMS_STATIC_XSS_FLAG WONDERCMS_REQUIRE_PRIVATE_FLAGS

web_pid=""
bot_pid=""
shutdown() {
    [ -z "$web_pid" ] || kill "$web_pid" 2>/dev/null || true
    [ -z "$bot_pid" ] || kill "$bot_pid" 2>/dev/null || true
    [ -z "$web_pid" ] || wait "$web_pid" 2>/dev/null || true
    [ -z "$bot_pid" ] || wait "$bot_pid" 2>/dev/null || true
}
trap shutdown TERM INT

su-exec www-data php -S 0.0.0.0:8080 -t /srv/wcms /srv/wcms/router.php &
web_pid=$!
su-exec wcmsbot /usr/bin/python3 /opt/wcms-bot/review_bot.py &
bot_pid=$!

# Keep the target healthy only while both the web application and review bot live.
while kill -0 "$web_pid" 2>/dev/null && kill -0 "$bot_pid" 2>/dev/null; do
    sleep 1
done

shutdown
exit 1
