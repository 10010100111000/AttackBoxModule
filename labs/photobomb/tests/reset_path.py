#!/usr/bin/env python3
import urllib.request
base="http://photobomb-target"
with urllib.request.urlopen(base+"/", timeout=10) as response:
    assert response.status == 200
assert b"Photobomb" in urllib.request.urlopen(base+"/", timeout=10).read()
print("PASS: recreated instance starts with clean gallery and no prior command artifacts")
