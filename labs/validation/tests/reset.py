#!/usr/bin/env python3
"""Fresh container restores registration without retaining per-instance state."""
import http.cookiejar
import urllib.error
import urllib.request

base = "http://validation-target"
with urllib.request.urlopen(base + "/", timeout=10) as response:
    assert b"Join the UHC - September Qualifiers" in response.read()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
with opener.open(base + "/account.php", timeout=10) as response:
    assert b"September Qualifiers" in response.read()
try:
    urllib.request.urlopen(base + "/validation-probe-reset-sentinel.txt", timeout=10)
    raise AssertionError("unexpected probe file survived reset")
except urllib.error.HTTPError as error:
    assert error.code == 404
print("PASS: recreated target has no registration session or previous probe file", flush=True)
