#!/usr/bin/env python3
import socket
import urllib.request

for url in ("http://127.0.0.1/healthz", "http://127.0.0.1:5000/"):
    with urllib.request.urlopen(url, timeout=3) as res:
        assert res.status == 200
with socket.create_connection(("127.0.0.1", 22), timeout=3) as conn:
    assert conn.recv(24).startswith(b"SSH-2.0-")
