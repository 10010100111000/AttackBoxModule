#!/usr/bin/python3.8
import os
import socket
import subprocess
import urllib.request

with urllib.request.urlopen("http://127.0.0.1/", timeout=3) as response:
    assert response.status == 200
for port, prefix in ((21, b"220"), (22, b"SSH-2.0-")):
    with socket.create_connection(("127.0.0.1", port), timeout=3) as sock:
        assert sock.recv(160).startswith(prefix)
assert os.path.isfile("/pcaps/0.pcap") and os.path.getsize("/pcaps/0.pcap") > 24
caps = subprocess.check_output(["getcap", "/usr/bin/python3.8"], text=True)
assert "cap_setuid" in caps
