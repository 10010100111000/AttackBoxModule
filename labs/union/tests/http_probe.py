#!/usr/bin/env python3
"""External smoke checks of ordinary routes and admission policy."""
import http.cookiejar
import socket
import urllib.parse
import urllib.request

host = "union-target"
base = "http://" + host
jar = http.cookiejar.CookieJar()
http = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def fetch(path, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    with http.open(base + path, data=body, timeout=10) as response:
        return response.status, response.read().decode("utf-8", "replace")

status, page = fetch("/")
assert status == 200
assert "Join the UHC - November Qualifiers" in page
assert "Player Eligibility Check" in page
assert "name=\"player\"" in page
assert fetch("/css/bootstrap.min.css")[0] == 200
print("PASS: original-style UHC registration page and local Bootstrap assets", flush=True)

_, known = fetch("/index.php", {"player": "ippsec"})
assert "Sorry, ippsec you are not eligible" in known
_, unknown = fetch("/index.php", {"player": "new-candidate"})
assert "Congratulations new-candidate" in unknown and "/challenge.php" in unknown
print("PASS: PHP queries real players table and follows original form behavior", flush=True)

assert "Qualifier Challenge" in fetch("/challenge.php")[1]
assert "Qualifier Challenge" in fetch("/challenge.php", {"flag": "invalid"})[1]
assert fetch("/firewall.php")[1].strip() == "Access Denied"
print("PASS: invalid qualifier cannot authorize the firewall page", flush=True)

try:
    with socket.create_connection((host, 22), timeout=2):
        raise AssertionError("SSH should not accept unauthenticated clients")
except (socket.timeout, TimeoutError, ConnectionRefusedError):
    pass
print("PASS: initial SSH network admission denied", flush=True)
