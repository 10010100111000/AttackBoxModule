#!/usr/bin/env bash
set -euo pipefail
image="${1:-ttp-pebbles:dev}"
container=""
cleanup() {
    if [[ -n "$container" ]]; then
        docker logs --tail 150 "$container" 2>&1 || true
        docker rm -f "$container" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT
container=$(docker run -d --network none --memory 1536m --pids-limit 512 "$image")
status=starting
for _ in $(seq 1 180); do
    state=$(docker inspect -f '{{.State.Status}}' "$container")
    [[ "$state" == running ]] || { echo "container exited: $state" >&2; exit 1; }
    status=$(docker inspect -f '{{.State.Health.Status}}' "$container")
    [[ "$status" == healthy ]] && break
    [[ "$status" == unhealthy ]] && { echo 'healthcheck failed' >&2; exit 1; }
    sleep 2
done
[[ "$status" == healthy ]] || { echo 'timeout waiting for authentic services' >&2; exit 1; }

docker exec "$container" bash /usr/local/bin/pebbles-healthcheck
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
docker cp "$here/source-contract.sh" "$container":/tmp/pebbles-source-contract.sh
docker exec "$container" bash /tmp/pebbles-source-contract.sh
html=$(docker exec "$container" curl -fsS http://127.0.0.1:80/)
grep -q '<title>Pebbles</title>' <<<"$html"
! grep -iq 'ZoneMinder' <<<"$html"
grants=$(docker exec "$container" mysql --user=zmuser --password=zmpass -Nse 'SHOW GRANTS FOR CURRENT_USER()')
grep -q 'ON \*\.\*' <<<"$grants"
docker exec "$container" sh -c 'test "$(ps -o user= -C mysqld | head -n 1 | xargs)" = root'
echo 'PASS: original port layout, packages and privileges'

if [[ "${PEBBLES_TEST_SQLI:-0}" == 1 ]]; then
    docker cp "$here/sqli-outfile-acceptance.sh" "$container":/tmp/pebbles-sqli-outfile-acceptance.sh
    docker exec "$container" bash /tmp/pebbles-sqli-outfile-acceptance.sh
fi
echo 'NOTE: full MySQL UDF root proof remains a separate required test'
