#!/bin/sh
set -eu

# User and Root Flags are baked into this versioned image by CI.
# Runtime startup never generates, rotates or accepts Flag environment variables.
for flag_file in /home/shelly/user.txt /root/root.txt; do
  if [ ! -s "$flag_file" ] || ! grep -Eq '^TTP\\{[a-z2-7]{16}\\}$' "$flag_file"; then
    echo "Shocker: missing or invalid baked Flag: $flag_file" >&2
    exit 1
  fi
done

chown shelly:shelly /home/shelly/user.txt
chmod 0644 /home/shelly/user.txt
chown root:root /root/root.txt
chmod 0600 /root/root.txt

mkdir -p /run/apache2 /run/sshd
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -e
exec /usr/sbin/httpd -DFOREGROUND
