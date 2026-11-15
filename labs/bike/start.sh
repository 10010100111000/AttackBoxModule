#!/bin/sh
set -eu

# Generate host keys on each new container creation rather than baking keys into image.
ssh-keygen -A >/dev/null 2>&1
/usr/sbin/sshd -t
/usr/sbin/sshd -e

# The Express process intentionally runs as root to reproduce the original lab.
exec node /root/Backend/server.js
