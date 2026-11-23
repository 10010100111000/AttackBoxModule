#!/usr/bin/env python3
"""External functional checks for the reconstructed bounty portal."""
import base64
import socket
import urllib.parse
import urllib.request

base = "http://bountyhunter-target"


def get(path):
    with urllib.request.urlopen(base + path, timeout=8) as response:
        return response.status, response.read().decode("utf-8", "replace")


def submit(xml):
    encoded = base64.b64encode(xml.encode("utf-8")).decode("ascii")
    data = urllib.parse.urlencode({"data": encoded}).encode()
    with urllib.request.urlopen(base + "/tracker_diRbPr00f314.php", data=data, timeout=8) as res:
        return res.status, res.read().decode("utf-8", "replace")


status, home = get("/")
assert status == 200 and "BOUNTY HUNTERS" in home
status, portal = get("/portal.php")
assert status == 200 and "under development" in portal and "/log_submit.php" in portal
status, form = get("/log_submit.php")
assert status == 200 and "Bounty Report System - Beta" in form
assert 'id="exploitTitle"' in form
assert "/resources/bountylog.js" in form
assert "tracker_diRbPr00f314.php" in get("/resources/bountylog.js")[1]
assert "Disable 'test' account" in get("/resources/README.txt")[1]
print("PASS: public site -> portal -> beta form -> hidden XML tracker discovery", flush=True)

xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<bugreport><title>First Report</title><cwe>CWE-79</cwe>"
    "<cvss>6.5</cvss><reward>250</reward></bugreport>"
)
status, confirmation = submit(xml)
assert status == 200 and "If DB were ready, would have added:" in confirmation
assert "First Report" in confirmation and "CWE-79" in confirmation
print("PASS: real PHP SimpleXML handles base64 XML form submission", flush=True)

with socket.create_connection(("bountyhunter-target", 22), timeout=6) as ssh:
    assert ssh.recv(64).startswith(b"SSH-2.0-")
print("PASS: real OpenSSH server visible on port 22", flush=True)

status, public_db = get("/db.php")
assert status == 200 and public_db.strip() == ""
print("PASS: browsable PHP credential config does not expose raw source", flush=True)
