#!/usr/bin/env bash
# Prove real answer provisioning is static, root-only and never required in GHCR layers.
set -Eeuo pipefail
image="${1:-ttp-pebbles:ci}"
cid=""
missing=""
cleanup() {
  for c in "$cid" "$missing"; do
    if [[ -n "$c" ]]; then docker rm -f "$c" >/dev/null 2>&1 || true; fi
  done
}
trap cleanup EXIT
private_flag='TTP{ci_private_static_test_0123456789}'
cid=$(docker run -d --network none --memory 1024m --pids-limit 256 --cpus 1 \
  -e PEBBLES_REQUIRE_STATIC_FLAG=1 \
  -e "PEBBLES_STATIC_ROOT_FLAG=$private_flag" "$image")
health=starting
for _ in $(seq 1 120); do
  state=$(docker inspect -f '{{.State.Status}}' "$cid")
  [[ "$state" == running ]] || { echo 'FAIL: static-flag instance exited unexpectedly' >&2; exit 1; }
  health=$(docker inspect -f '{{.State.Health.Status}}' "$cid")
  [[ "$health" == healthy ]] && break
  [[ "$health" == unhealthy ]] && { echo 'FAIL: static-flag instance unhealthy' >&2; exit 1; }
  sleep 2
done
[[ "$health" == healthy ]] || { echo 'FAIL: static-flag startup timed out' >&2; exit 1; }
test "$(docker exec "$cid" cat /root/proof.txt)" = "$private_flag"
if docker exec --user www-data "$cid" test -r /root/proof.txt; then
  echo 'FAIL: www-data can read the root-only static answer' >&2
  exit 1
fi
# The actual Worker lifecycle deletes a target container on stop and creates a
# new container on start. Verify the same private static answer is injected
# into each fresh instance; do not require in-place docker restart.
docker rm -f "$cid" >/dev/null
cid=$(docker run -d --network none --memory 1024m --pids-limit 256 --cpus 1 \
  -e PEBBLES_REQUIRE_STATIC_FLAG=1 \
  -e "PEBBLES_STATIC_ROOT_FLAG=$private_flag" "$image")
health=starting
for _ in $(seq 1 120); do
  state=$(docker inspect -f '{{.State.Status}}' "$cid")
  [[ "$state" == running ]] || { echo 'FAIL: recreated static-flag instance exited' >&2; exit 1; }
  health=$(docker inspect -f '{{.State.Health.Status}}' "$cid")
  [[ "$health" == healthy ]] && break
  [[ "$health" == unhealthy ]] && { echo 'FAIL: recreated static-flag instance unhealthy' >&2; exit 1; }
  sleep 2
done
[[ "$health" == healthy ]] || { echo 'FAIL: recreated instance did not become healthy' >&2; exit 1; }
test "$(docker exec "$cid" cat /root/proof.txt)" = "$private_flag"
if docker exec --user www-data "$cid" test -r /root/proof.txt; then
  echo 'FAIL: private proof readable by www-data after fresh start' >&2
  exit 1
fi
missing=$(docker run -d --network none --memory 1024m --pids-limit 256 --cpus 1 \
  -e PEBBLES_REQUIRE_STATIC_FLAG=1 "$image")
for _ in $(seq 1 20); do
  [[ "$(docker inspect -f '{{.State.Status}}' "$missing")" == exited ]] && break
  sleep 1
done
[[ "$(docker inspect -f '{{.State.Status}}' "$missing")" == exited ]] || { echo 'FAIL: missing Flag was accepted' >&2; exit 1; }
[[ "$(docker inspect -f '{{.State.ExitCode}}' "$missing")" != 0 ]] || { echo 'FAIL: missing Flag exited successfully' >&2; exit 1; }
echo 'PASS: Worker-compatible static private Flag replaces demo, stays root-only across fresh instances and fails closed'
