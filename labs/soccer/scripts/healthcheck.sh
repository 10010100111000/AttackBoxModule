#!/bin/sh
set -eu
curl -fsS --max-time 3 -H 'Host: soccer.htb' http://127.0.0.1:8080/ >/dev/null
curl -fsS --max-time 3 -H 'Host: soc-player.soccer.htb' http://127.0.0.1:8080/healthz >/dev/null
