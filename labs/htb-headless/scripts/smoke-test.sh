#!/bin/sh
# Non-exploit integration checks for the intended application/runtime flow.
# This script deliberately uses only a harmless report marker and normal form data.
set -eu

base="http://127.0.0.1:5000"
marker="TTP_HEADLESS_CI_REPORT_MARKER"

curl -fsS "$base/" | grep -qi "UNDER CONSTRUCTION"
curl -fsS "$base/support" | grep -q "Contact Support"

code=$(curl -sS -o /dev/null -w "%{http_code}" \
  -H "Cookie: is_admin=InVzZXIi.uAlmXlTvm8vyihjNaPDWnvB_Zfs" \
  "$base/dashboard")
test "$code" = "401"

# Submit an ordinary support report with a harmless User-Agent marker. This
# exercises form handling, report persistence and the real Chromium reviewer;
# it does not submit script, HTML, XSS, command or shell payloads.
curl -fsS -A "$marker" \
  --data-urlencode "fname=CI" \
  --data-urlencode "lname=Smoke" \
  --data-urlencode "email=ci@example.invalid" \
  --data-urlencode "phone=0000000000" \
  --data-urlencode "message=Please review this ordinary support request" \
  "$base/support" >/tmp/headless-support-response.html

report_file=""
for candidate in /home/dvir/app/hacking_reports/*.html; do
  if [ -f "$candidate" ] && grep -q "$marker" "$candidate"; then
    report_file="$candidate"
    break
  fi
done
test -n "$report_file"
report_name=$(basename "$report_file")

# Wait for Chromium to fetch and render the stored report, not merely for its
# process to exist. The reviewer writes this marker only after checking the DOM.
attempt=0
while [ "$attempt" -lt 20 ]; do
  if [ -s /tmp/headless-last-reviewed-report ] && \
     grep -Fxq "$report_name" /tmp/headless-last-reviewed-report; then
    break
  fi
  attempt=$((attempt + 1))
  sleep 1
done
grep -Fxq "$report_name" /tmp/headless-last-reviewed-report

# Exercise the ordinary dashboard/report-helper path with the known public
# reference admin cookie and a normal date. No command metacharacters are sent.
curl -fsS -b "is_admin=ImFkbWluIg.dmzDkZNEm6CK0oyL1fbM-SnXpH0" \
  --data-urlencode "date=2023-09-15" "$base/dashboard" | \
  grep -q "Systems are up and running!"

# Validate the service account, filesystem layout, static Flags and sudo policy.
test "$(id -u dvir)" = "1000"
test -w /home/dvir/app
test -s /home/dvir/user.txt
test -s /root/root.txt
test "$(stat -c '%U:%a' /home/dvir/user.txt)" = "dvir:400"
test "$(stat -c '%U:%a' /root/root.txt)" = "root:600"
test -x /usr/bin/syscheck
grep -Fq './initdb.sh' /usr/bin/syscheck
visudo -cf /etc/sudoers >/dev/null
sudo -l -U dvir | grep -Fq '/usr/bin/syscheck'
ps -eo user,args | grep -E '[a]pp.py' | grep -q '^dvir'
pgrep -f '[i]nspect_reports.py' >/dev/null
ss -lnt | grep -q ':22 '

echo "PASS: Headless non-exploit application/runtime integration checks"
