#!/usr/bin/env python3
"""A recreated instance should have no PHP session or SSH admission state."""
import socket
import urllib.request

host = "union-target"
with urllib.request.urlopen("http://" + host + "/", timeout=10) as result:
    assert b"Player Eligibility Check" in result.read()
with urllib.request.urlopen("http://" + host + "/firewall.php", timeout=10) as result:
    assert result.read().strip() == b"Access Denied"
try:
    with socket.create_connection((host, 22), timeout=2):
        raise AssertionError("SSH is open after instance recreation")
except (socket.timeout, TimeoutError, ConnectionRefusedError):
    pass
print("PASS: new Union instance resets its session and network state", flush=True)
