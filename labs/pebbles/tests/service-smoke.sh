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
if [[ "${PEBBLES_TEST_UDF:-0}" == 1 ]]; then
    # Create helper image only in CI; production runtime never contains UDF source or binary.
    tool_container=$(docker create ttp-pebbles-udf:ci)
    helper_dir=$(mktemp -d)
    docker cp "$tool_container":/tmp/ttp_udf_probe.so "$helper_dir/ttp_udf_probe.so"
    docker rm -f "$tool_container" >/dev/null
    docker cp "$helper_dir/ttp_udf_probe.so" "$container":/tmp/ttp_udf_probe.so
    rm -rf "$helper_dir"
    docker cp "$here/udf-acceptance.sh" "$container":/tmp/pebbles-udf-acceptance.sh
    expected_sha256=$(sha256sum "$here/../flags/root.txt" | cut -d' ' -f1)
    docker exec --user www-data --env "PEBBLES_EXPECTED_ROOT_SHA256=$expected_sha256" "$container" bash /tmp/pebbles-udf-acceptance.sh
else
    echo 'NOTE: MySQL UDF root escalation is not tested unless PEBBLES_TEST_UDF=1'
fi
