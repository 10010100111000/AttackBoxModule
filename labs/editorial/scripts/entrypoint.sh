#!/bin/sh
set -eu
required=${EDITORIAL_REQUIRE_PRIVATE_FLAGS:-0}
user_flag=${EDITORIAL_STATIC_USER_FLAG:-}
root_flag=${EDITORIAL_STATIC_ROOT_FLAG:-}
if [ "$required" = "1" ] && { [ -z "$user_flag" ] || [ -z "$root_flag" ]; }; then
    echo "Editorial: private instance flags required" >&2
    exit 1
fi
if [ -n "$user_flag" ]; then
    umask 077
    printf '%s\n' "$user_flag" > /home/dev/user.txt
    chown dev:dev /home/dev/user.txt
    chmod 0640 /home/dev/user.txt
fi
if [ -n "$root_flag" ]; then
    umask 077
    printf '%s\n' "$root_flag" > /root/root.txt
    chmod 0600 /root/root.txt
fi
unset required user_flag root_flag EDITORIAL_REQUIRE_PRIVATE_FLAGS EDITORIAL_STATIC_USER_FLAG EDITORIAL_STATIC_ROOT_FLAG
umask 022
mkdir -p /run/sshd /var/www/editorial/uploads
chown www-data:www-data /var/www/editorial/uploads
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -D -e &
su -s /bin/sh www-data -c "cd /opt/editorial && exec /usr/local/bin/gunicorn -w 1 -b 127.0.0.1:8000 public_app:app" &
su -s /bin/sh dev -c "cd /opt/editorial && exec /usr/local/bin/gunicorn -w 1 -b 127.0.0.1:5000 api_app:app" &
exec /usr/sbin/nginx -g 'daemon off;'
