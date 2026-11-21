#!/usr/bin/env bash
# Validate ephemeral one-container-per-learner lifecycle in Docker.
# This is a reset/isolation test, not an exploit or player-facing guide.
set -Eeuo pipefail

image="${1:-ttp-pebbles:ci}"
first=""
second=""
cleanup() {
  for container in "$first" "$second"; do
    if [[ -n "$container" ]]; then
      if [[ "${PEBBLES_DEBUG_RESET:-0}" == 1 ]]; then docker logs --tail 60 "$container" >&2 || true; fi
      docker rm -f "$container" >/dev/null 2>&1 || true
    fi
  done
}
trap cleanup EXIT

new_instance() {
  docker run -d --network none --memory 1024m --pids-limit 256 --cpus 1 "$image"
}
wait_healthy() {
  local container="$1" health="starting" state="unknown"
  for _ in $(seq 1 120); do
    state=$(docker inspect -f '{{.State.Status}}' "$container")
    [[ "$state" == running ]] || { echo "FAIL: container $container state $state" >&2; return 1; }
    health=$(docker inspect -f '{{.State.Health.Status}}' "$container")
    [[ "$health" == healthy ]] && return 0
    [[ "$health" == unhealthy ]] && { echo "FAIL: unhealthy $container" >&2; return 1; }
    sleep 2
  done
  echo "FAIL: timeout waiting for container health ($container)" >&2
  return 1
}
table_count() {
  docker exec "$1" mysql --user=zmuser --password=zmpass -D zm -Nse     "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='zm' AND table_name='ttp_reset_marker'"     2>/dev/null
}
root_proof_hash() {
  docker exec "$1" sha256sum /root/proof.txt | awk '{print $1}'
}

first=$(new_instance)
wait_healthy "$first"
[[ "$(table_count "$first")" == 0 ]] || { echo "FAIL: initial SQL state not clean" >&2; exit 1; }
first_hash=$(root_proof_hash "$first")

# Add persistent state to the actual MySQL volume and the real Apache document
# root. We deliberately do NOT delete these test artifacts inside the instance.
docker exec "$first" mysql --user=zmuser --password=zmpass -D zm -e   'CREATE TABLE ttp_reset_marker (id INTEGER PRIMARY KEY, note VARCHAR(40))' >/dev/null 2>&1
docker exec "$first" sh -c 'printf "instance-state" > /var/www/html/ttp-reset-marker.txt'
[[ "$(table_count "$first")" == 1 ]] || { echo "FAIL: SQL state marker missing" >&2; exit 1; }
docker exec "$first" test -f /var/www/html/ttp-reset-marker.txt

# Restart preserves that user's state. Reset is achieved by deleting the
# container and creating a fresh instance from the immutable image.
docker restart --time 15 "$first" >/dev/null
wait_healthy "$first"
[[ "$(table_count "$first")" == 1 ]] || { echo "FAIL: state disappeared on restart" >&2; exit 1; }
docker exec "$first" test -f /var/www/html/ttp-reset-marker.txt

docker rm -f "$first" >/dev/null
first=""
second=$(new_instance)
wait_healthy "$second"
[[ "$(table_count "$second")" == 0 ]] || { echo "FAIL: previous learner's SQL state survived reset" >&2; exit 1; }
if docker exec "$second" test -e /var/www/html/ttp-reset-marker.txt; then
  echo "FAIL: previous learner's file survived reset" >&2
  exit 1
fi
[[ "$(root_proof_hash "$second")" == "$first_hash" ]] || {
  echo "FAIL: static proof is inconsistent across fresh instances" >&2
  exit 1
}
docker exec "$second" sh -c 'test -s /root/proof.txt && test "$(stat -c %a /root/proof.txt)" = 600'
echo 'PASS: restart preserves instance state; new container resets DB and files; static proof remains consistent'
