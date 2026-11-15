#!/usr/bin/env bash
set -Eeuo pipefail
container="${1:-funnel-lab}"
docker inspect --format '{{.State.Health.Status}}' "$container"
docker exec "$container" /usr/local/bin/funnel-healthcheck
docker exec "$container" bash -c "ss -ltn 2>/dev/null | grep 127.0.0.1:5432" || \
  docker exec "$container" bash -c "grep -E '^[[:space:]]*listen_addresses' /etc/postgresql/15/main/postgresql.conf"
echo 'Service checks passed. Confirm SSH and FTP externally using the README commands.'
