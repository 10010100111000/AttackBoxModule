#!/usr/bin/env bash
# Tests services only; actual SQLi and UDF are separate acceptance checks.
set -euo pipefail

dpkg-query -W -f='${Version}' zoneminder | grep -Fxq '1.29.0+dfsg-1ubuntu2'
pid=$(pgrep -xo mysqld)
[[ -n "$pid" ]]
[[ $(stat -c '%u' "/proc/$pid") -eq 0 ]]
mysql --protocol=socket --user=zmuser --password=zmpass -D zm -Nse 'SELECT COUNT(*) FROM Logs' >/dev/null 2>&1
for port in 21 22 80 3305 8080; do
    nc -z -w 3 127.0.0.1 "$port" >/dev/null 2>&1
done
curl -fsS --max-time 5 http://127.0.0.1:80/ | grep -q 'Pebbles'
curl -fsS --max-time 5 http://127.0.0.1:3305/ | grep -q 'Apache2 Ubuntu Default Page'
curl -fsS --max-time 5 http://127.0.0.1:3305/zm/index.php | grep -qi 'ZoneMinder'
curl -fsS --max-time 7 http://127.0.0.1:8080/ | grep -qi 'Tomcat'
test -s /root/proof.txt
