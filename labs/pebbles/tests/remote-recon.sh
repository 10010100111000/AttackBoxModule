#!/usr/bin/env bash
# Verify the exact observable attack surface from a SECOND isolated container.
# No host ports are published and the Docker bridge has no external route.
set -Eeuo pipefail
image="$1"
network="ttp-pebbles-scan-$RANDOM-$$"
target="ttp-pebbles-ctf-$RANDOM-$$"
cid=""
network_created=0
cleanup() {
  if [[ -n "$cid" ]]; then docker logs --tail 45 "$cid" >&2 || true; docker rm -f "$cid" >/dev/null 2>&1 || true; fi
  if [[ "$network_created" == 1 ]]; then docker network rm "$network" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT

docker image inspect python:3.12-alpine >/dev/null 2>&1 || docker pull python:3.12-alpine
docker network create --driver bridge --internal "$network" >/dev/null
network_created=1
cid=$(docker run -d --name "$target" --network "$network" --network-alias pebbles-target \
  --memory 1536m --pids-limit 512 --cpus 1 "$image")
health=starting
for _ in $(seq 1 90); do
  state=$(docker inspect -f '{{.State.Status}}' "$cid")
  [[ "$state" == running ]] || { echo "FAIL: target exited during external recon" >&2; exit 1; }
  health=$(docker inspect -f '{{.State.Health.Status}}' "$cid")
  if [[ "$health" == healthy ]]; then break; fi
  if [[ "$health" == unhealthy ]]; then echo 'FAIL: Docker healthcheck failed' >&2; exit 1; fi
  sleep 2
done
[[ "$health" == healthy ]] || { echo 'FAIL: target did not become healthy' >&2; exit 1; }

docker run --rm -i --network "$network" python:3.12-alpine python - <<'PY'
import socket
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HOST = "pebbles-target"

def reachable(port):
    try:
        with socket.create_connection((HOST, port), timeout=4):
            return True
    except OSError:
        return False

def fetch(port, path="/", method="GET", data=None):
    req = Request(f"http://{HOST}:{port}{path}", data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urlopen(req, timeout=8) as response:
            return response.status, response.read(262144).decode("utf-8", "replace")
    except HTTPError as exc:
        return exc.code, exc.read(262144).decode("utf-8", "replace")

observed = [p for p in (21, 22, 80, 3305, 8080) if reachable(p)]
assert observed == [21, 22, 80, 3305, 8080], f"Missing original visible service(s): {observed}"

for port, prefix in ((21, b"220"), (22, b"SSH-2.0")):
    with socket.create_connection((HOST, port), timeout=5) as sock:
        sock.settimeout(5)
        banner = sock.recv(256)
    assert banner.startswith(prefix), f"{port} unexpected banner {banner!r}"

for port in (3306, 8009, 18080):
    assert not reachable(port), f"Unexpected externally accessible private service: {port}"

status, front = fetch(80)
assert status == 200 and "Pebbles" in front, "PHP landing page missing"
assert "ZoneMinder" not in front and "/zm/" not in front, "Decoy leaks hidden application"
status, login = fetch(80, "/", method="POST", data=b"username=admin&password=admin")
assert status == 200 and "Invalid username or password" in login, "Decoy login not functional"
status, hidden = fetch(80, "/zm/index.php")
assert status == 200 and "ZoneMinder" in hidden, "Original unlinked ZoneMinder path missing from port 80"

status, default = fetch(3305)
assert status == 200 and "Apache2 Ubuntu Default Page" in default, "Initial default Apache page is missing"
status, zoneminder = fetch(3305, "/zm/index.php")
assert status == 200 and "ZoneMinder" in zoneminder, "Genuine ZoneMinder was not discoverable on 3305/zm/"

status, tomcat = fetch(8080)
assert status == 200 and "Tomcat" in tomcat, "Native Apache Tomcat 9 console not visible"
print("PASS: attacker-side port enumeration, unlinked /zm/ on both Apache ports, native Tomcat, private-only DB/AJP")
PY
