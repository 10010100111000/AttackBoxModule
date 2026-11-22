#!/usr/bin/env python3
import urllib.error
import urllib.request
base="http://cap-target"
with urllib.request.urlopen(base+"/", timeout=8) as response:
    assert response.status == 200
with urllib.request.urlopen(base+"/download/0", timeout=8) as response:
    assert response.status == 200
try:
    urllib.request.urlopen(base+"/download/1", timeout=8)
except urllib.error.HTTPError as err:
    assert err.code == 404
else:
    raise AssertionError("dynamic capture survived container recreation")
print("PASS: seed PCAP restored and dynamic capture removed after recreate")
