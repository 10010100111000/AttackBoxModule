#!/usr/bin/env bash
# Validate independent Docker learner instances and Worker-style stop/create reset.
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
diagnose() {
  local container="$1"
  echo "Container failure details:" >&2
  docker inspect --format 'state={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}} error={{.State.Error}}' "$container" >&2 || true
  docker logs --tail 100 "$container" >&2 || true
}
wait_healthy() {
  local container="$1" health="starting" state="unknown"
  for _ in $(seq 1 120); do
    state=$(docker inspect -f '{{.State.Status}}' "$container")
    [[ "$state" == running ]] || { echo "FAIL: container $container state $state" >&2; diagnose "$container"; return 1; }
    health=$(docker inspect -f '{{.State.Health.Status}}' "$container")
    [[ "$health" == healthy ]] && return 0
    [[ "$health" == unhealthy ]] && { echo "FAIL: unhealthy $container" >&2; diagnose "$container"; return 1; }
    sleep 2
  done
  echo "FAIL: timeout waiting for container health ($container)" >&2
  diagnose "$container"
  return 1
}
table_count() {
  docker exec "$1" mysql --user=zmuser --password=zmpass -D zm -Nse     "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='zm' AND table_name='ttp_reset_marker'"     2>/dev/null
}
root_proof_hash() {
  docker exec "$1" sha256sum /root/proof.txt | awk '{print $1}'
}

echo '[reset] starting first instance'
first=$(new_instance)
wait_healthy "$first"
echo '[reset] first instance healthy'
[[ "$(table_count "$first")" == 0 ]] || { echo "FAIL: initial SQL state not clean" >&2; exit 1; }
first_hash=$(root_proof_hash "$first")

# Add persistent state to the actual MySQL volume and the real Apache document
# root. We deliberately do NOT delete these test artifacts inside the instance.
docker exec "$first" mysql --user=zmuser --password=zmpass -D zm -e   'CREATE TABLE ttp_reset_marker (id INTEGER PRIMARY KEY, note VARCHAR(40))' >/dev/null 2>&1
docker exec "$first" sh -c 'printf "instance-state" > /var/www/html/ttp-reset-marker.txt'
[[ "$(table_count "$first")" == 1 ]] || { echo "FAIL: SQL state marker missing" >&2; exit 1; }
docker exec "$first" test -f /var/www/html/ttp-reset-marker.txt

echo '[reset] seeded database and filesystem'
# Worker.stop removes the container and volumes. Worker.start creates a fresh
# container. Docker restart of the SAME container is not part of the platform's
# current lifecycle contract, so we deliberately do not require it here.
echo '[reset] starting a second independent learner instance'
second=$(new_instance)
wait_healthy "$second"
echo '[reset] second learner instance healthy'
[[ "$(table_count "$second")" == 0 ]] || { echo "FAIL: first learner's SQL state leaked to second" >&2; exit 1; }
if docker exec "$second" test -e /var/www/html/ttp-reset-marker.txt; then
  echo "FAIL: first learner's file leaked to second learner" >&2
  exit 1
fi
[[ "$(root_proof_hash "$second")" == "$first_hash" ]] || {
  echo "FAIL: static proof inconsistent between independent learners" >&2
  exit 1
}
[[ "$(table_count "$first")" == 1 ]] || { echo "FAIL: first learner's SQL state unexpectedly cleared" >&2; exit 1; }
docker exec "$first" test -f /var/www/html/ttp-reset-marker.txt

echo '[reset] deleting first instance to match Worker stop'
docker rm -f "$first" >/dev/null
first=""
echo '[reset] starting a fresh instance to match Worker start'
first=$(new_instance)
wait_healthy "$first"
echo '[reset] newly created first learner instance healthy'
[[ "$(table_count "$first")" == 0 ]] || { echo "FAIL: old SQL state survived a fresh container" >&2; exit 1; }
if docker exec "$first" test -e /var/www/html/ttp-reset-marker.txt; then
  echo "FAIL: previous learner's file survived fresh container creation" >&2
  exit 1
fi
[[ "$(root_proof_hash "$first")" == "$first_hash" ]] || {
  echo "FAIL: static root proof changed across fresh instances" >&2
  exit 1
}
docker exec "$first" sh -c 'test -s /root/proof.txt && test "$(stat -c %a /root/proof.txt)" = 600'
echo 'PASS: independent learner instances; Worker-style stop/delete and fresh start reset DB and files; static proof consistent'
