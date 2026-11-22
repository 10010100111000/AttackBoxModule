#!/usr/bin/env python3
import os, urllib.request
base=os.environ.get("TARGET_URL","http://shocker-target")
with urllib.request.urlopen(base+"/cgi-bin/user.sh", timeout=10) as x:
    text=x.read().decode(errors="replace")
assert "Just an uptime test script" in text
print("PASS: native CGI restarted cleanly in fresh container")
