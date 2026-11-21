#!/usr/bin/env bash
# Debian-only CI proof. An actual vulnerable instance, never external/public.
set -Eeuo pipefail
image="$1"
here=$(cd -- "$(dirname -- "$0")" && pwd)
lab=$(cd "$here/../.." && pwd)
cid=""
helper=""
tmpdir=""
cleanup() {
    if [[ -n "$cid" ]]; then docker logs --tail 60 "$cid" >&2 || true; docker rm -f "$cid" >/dev/null 2>&1 || true; fi
    if [[ -n "$helper" ]]; then docker rm -f "$helper" >/dev/null 2>&1 || true; fi
    if [[ -n "$tmpdir" ]]; then rm -rf "$tmpdir"; fi
}
trap cleanup EXIT
cid=$(docker run -d --network none --memory 1536m --pids-limit 512 --cpus 1 "$image")
health=starting
for _ in $(seq 1 100); do
  state=$(docker inspect -f '{{.State.Status}}' "$cid")
  if [[ "$state" != running ]]; then echo "FAIL: real Debian services exited: $state" >&2; exit 1; fi
  health=$(docker inspect -f '{{.State.Health.Status}}' "$cid")
  [[ "$health" == healthy ]] && break
  if [[ "$health" == unhealthy ]]; then echo "FAIL: genuine services are unhealthy" >&2; exit 1; fi
  sleep 2
done
[[ "$health" == healthy ]] || { echo 'FAIL: timeout waiting for real services' >&2; exit 1; }
docker cp "$lab/debian/source-contract.sh" "$cid":/tmp/debian-source-contract.sh
docker exec "$cid" bash /tmp/debian-source-contract.sh

# Drive the genuine ZoneMinder log.php limit SQL injection.
docker cp "$lab/tests/sqli-outfile-acceptance.sh" "$cid":/tmp/pebbles-sqli-outfile-acceptance.sh
docker exec "$cid" bash /tmp/pebbles-sqli-outfile-acceptance.sh

# Compile a real Debian-glibc compatible library in a separate CI-only image.
helper=$(docker create ttp-pebbles-udf-debian:ci)
tmpdir=$(mktemp -d)
docker cp "$helper":/tmp/ttp_udf_probe.so "$tmpdir/ttp_udf_probe.so"
docker rm -f "$helper" >/dev/null
helper=""
docker cp "$tmpdir/ttp_udf_probe.so" "$cid":/tmp/ttp_udf_probe.so
docker cp "$lab/tests/udf-acceptance.sh" "$cid":/tmp/pebbles-udf-acceptance.sh
expected_sha256=$(sha256sum "$lab/flags/root.txt" | cut -d' ' -f1)
docker exec --user www-data --env "PEBBLES_EXPECTED_ROOT_SHA256=$expected_sha256" \
  "$cid" bash /tmp/pebbles-udf-acceptance.sh
echo 'PASS: Debian genuine ZoneMinder SQLi and Debian-compatible UDF root chain'
