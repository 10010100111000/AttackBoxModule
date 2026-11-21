#!/usr/bin/env bash
# Diagnostic only. Samples real multi-service Docker startup on a short-lived CI host.
set -Eeuo pipefail
image="${1:-ttp-pebbles:ci}"
bytes=$(docker image inspect --format '{{.Size}}' "$image")
mib=$(awk -v b="$bytes" 'BEGIN {printf "%.1f", b/1048576}')
report() {
  printf "%s\n" "$1"
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then printf "%s\n" "$1" >> "$GITHUB_STEP_SUMMARY"; fi
}
report "### Pebbles Docker resource profile"
report "Image size: ${mib} MiB (${bytes} bytes); Linux amd64, all original services."
profile() {
  local ram="$1" pids="$2" label="$3" cid="" state="unknown" health="starting" usage=""
  report ""
  report "Profile: $label — ${ram} MiB, ${pids} PIDs, 1 CPU"
  if ! cid=$(docker run -d --network none --memory "${ram}m" --pids-limit "$pids" --cpus 1 "$image" 2>&1); then
    report "Startup failed: $cid"
    return 0
  fi
  for _ in $(seq 1 65); do
    state=$(docker inspect -f '{{.State.Status}}' "$cid")
    [[ "$state" == running ]] || break
    health=$(docker inspect -f '{{.State.Health.Status}}' "$cid")
    [[ "$health" == healthy || "$health" == unhealthy ]] && break
    sleep 2
  done
  if [[ "$state" == running && "$health" == healthy ]]; then
    usage=$(docker stats --no-stream --format '{{.MemUsage}}' "$cid" || true)
    count=$(docker stats --no-stream --format '{{.PIDs}}' "$cid" || true)
    cpu=$(docker stats --no-stream --format '{{.CPUPerc}}' "$cid" || true)
    report "Result: HEALTHY. Memory: $usage; process count: $count; CPU snapshot: $cpu"
  else
    killed=$(docker inspect -f '{{.State.OOMKilled}}' "$cid" || true)
    report "Result: NOT HEALTHY. State: $state; health: $health; OOMKilled: $killed"
    docker logs --tail 25 "$cid" >&2 || true
  fi
  docker rm -f "$cid" >/dev/null 2>&1 || true
}
profile 512 256 "Current Worker defaults"
profile 1536 512 "Pebbles development allowance"
report ""
report "Snapshots from CI only; production Worker isolation and resource use remain unverified."
