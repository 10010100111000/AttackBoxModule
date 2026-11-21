#!/bin/sh
set -eu
private=$(printenv NIBBLES_REQUIRE_PRIVATE_FLAGS || true)
user_flag=$(printenv NIBBLES_STATIC_USER_FLAG || true)
root_flag=$(printenv NIBBLES_STATIC_ROOT_FLAG || true)
if [ "$private" = 1 ] && { [ -z "$user_flag" ] || [ -z "$root_flag" ]; }; then
    echo "Nibbles: private static user/root flags required" >&2
    exit 1
fi
if [ -n "$user_flag" ]; then
    umask 077
    printf '%s\n' "$user_flag" > /home/nibbler/user.txt
    chown nibbler:nibbler /home/nibbler/user.txt
    chmod 0644 /home/nibbler/user.txt
fi
if [ -n "$root_flag" ]; then
    umask 077
    printf '%s\n' "$root_flag" > /root/root.txt
    chown root:root /root/root.txt
    chmod 0600 /root/root.txt
fi
unset user_flag root_flag private NIBBLES_STATIC_USER_FLAG NIBBLES_STATIC_ROOT_FLAG NIBBLES_REQUIRE_PRIVATE_FLAGS
mkdir -p /run/sshd /run/apache2
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -e
exec /usr/sbin/httpd -DFOREGROUND
