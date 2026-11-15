#!/bin/sh
set -eu

mkdir -p /var/run/sshd
ssh-keygen -A
/usr/sbin/sshd -t
/usr/sbin/sshd

# The upload directory must be writable by Apache's www-data account.
chown -R www-data:www-data /var/www/html/_uploaded
chmod 0755 /var/www/html/_uploaded

exec apache2-foreground
