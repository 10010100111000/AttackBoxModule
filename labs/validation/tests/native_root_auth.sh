#!/bin/sh
# Actual Unix password authentication from the unprivileged Apache identity.
set -eu
test "$(id -un)" = apache
test ! -r /root/root.txt
test -n "$VALIDATION_CI_ROOT_PASSWORD"
set +e
output=$(
  ( sleep 2; printf '%s\n' "$VALIDATION_CI_ROOT_PASSWORD" ) |
    script -q -e -c 'su -c "id; cat /root/root.txt" root' /dev/null
)
result=$?
set -e
if [ "$result" -ne 0 ]; then
  printf 'Native password authentication failed with exit code %s\n' "$result" >&2
  printf 'su output: %s\n' "$output" >&2
  id >&2
  ls -l "$(command -v su)" >&2
  exit "$result"
fi
normalized=$(printf '%s\n' "$output" | tr -d '\r')
printf '%s\n' "$normalized" | grep -F 'uid=0(root)' >/dev/null
printf '%s\n' "$normalized" | grep -F 'TTP{validation_ci_private_root_0123456789}' >/dev/null
printf '%s\n' 'PASS: real Unix su password reuse returns UID 0 and the root flag'
