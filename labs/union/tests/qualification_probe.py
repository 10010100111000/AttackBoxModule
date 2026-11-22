#!/usr/bin/env python3
"""Functional verification of a valid qualifier, session, SSH firewall and login."""
import http.cookiejar
import os
import socket
import subprocess
import urllib.parse
import urllib.request

host = "union-target"
base = "http://" + host
token = os.environ["UNION_TEST_QUALIFIER"]
assert token.startswith("UHC{") and token.endswith("}")

cookies = http.cookiejar.CookieJar()
browser = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))

def page(path, values=None):
    data = urllib.parse.urlencode(values).encode() if values is not None else None
    with browser.open(base + path, data=data, timeout=10) as response:
        return response.status, response.read().decode("utf-8", "replace")

def can_connect():
    try:
        with socket.create_connection((host, 22), timeout=2) as sock:
            return sock.recv(32).startswith(b"SSH-2.0-")
    except (OSError, TimeoutError):
        return False

assert not can_connect(), "SSH must be restricted before admission"
assert "Qualifier Challenge" in page("/challenge.php")[1]
assert "Qualifier Challenge" in page("/challenge.php", {"flag": "UHC{invalid}"})[1]
assert not can_connect(), "Invalid qualifier must not open SSH"
print("PASS: invalid qualifier cannot open SSH", flush=True)

status, admitted = page("/challenge.php", {"flag": token})
assert status == 200 and "Your IP Address has now been granted SSH Access." in admitted
assert can_connect(), "Valid qualifier did not open native SSH gate"
print("PASS: real PHP session and iptables admission allow SSH", flush=True)

result = subprocess.run(
    [
        "sshpass", "-p", "uhc-11qual-global-pw", "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "PreferredAuthentications=password",
        "-o", "PubkeyAuthentication=no",
        "-o", "ConnectTimeout=5",
        "uhc@" + host, "id -un",
    ],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15, check=True,
)
assert result.stdout.decode().strip() == "uhc"
print("PASS: normal OpenSSH password login as uhc over permitted client IP", flush=True)
