#!/bin/sh
set -eu
test -s /home/shelly/user.txt
test -s /root/root.txt
wget -q -T 3 -O /dev/null http://127.0.0.1/
output=$(wget -q -T 5 -O - http://127.0.0.1/cgi-bin/user.sh)
case "$output" in *'Just an uptime test script'*) : ;; *) exit 1 ;; esac
pidof sshd >/dev/null
