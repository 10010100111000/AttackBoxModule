#!/usr/bin/env bash
set -Eeuo pipefail
# Check service responses, not only whether the parent container process exists.
check_banner() {
  local port="$1" expected="$2" line
  exec 3<>"/dev/tcp/127.0.0.1/$port"
  IFS= read -r -t 3 line <&3
  exec 3<&- 3>&-
  [[ "$line" == "$expected"* ]]
}
check_banner 21 '220'
check_banner 22 'SSH-2.0-'
pg_isready -q -h 127.0.0.1 -p 5432
runuser -u postgres -- psql -qAt -d secrets -c 'SELECT count(*) FROM public.flag;' | grep -qx 1
