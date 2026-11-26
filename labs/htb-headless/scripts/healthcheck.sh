#!/bin/sh
set -eu
curl -fsS --max-time 4 http://127.0.0.1:5000/ >/dev/null
curl -fsS --max-time 4 http://127.0.0.1:5000/support | grep -qi "Contact Support"
pgrep -f '[i]nspect_reports.py' >/dev/null
ss -lnt | grep -q ':22 '
