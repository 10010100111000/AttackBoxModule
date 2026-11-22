#!/bin/sh
# Actual Unix password authentication from the unprivileged Apache identity.
set -eu
test "$(id -un)" = apache
test ! -r /root/root.txt
test -n "$VALIDATION_CI_ROOT_PASSWORD"
output=$(
  printf '%s\n' "$VALIDATION_CI_ROOT_PASSWORD" |
    script -q -e -c 'su -c "id -u; cat /root/root.txt" root' /dev/null
)
normalized=$(printf '%s\n' "$output" | tr -d '\r')
printf '%s\n' "$normalized" | grep -Fx '0' >/dev/null
printf '%s\n' "$normalized" | grep -F 'TTP{validation_ci_private_root_0123456789}' >/dev/null
printf '%s\n' 'PASS: real Unix su password reuse returns UID 0 and the root flag'
