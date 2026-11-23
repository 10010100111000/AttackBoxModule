#!/usr/bin/env python3
"""External integration check: eligibility form actually delegates to MariaDB SQL."""
import urllib.parse
import urllib.request

url = "http://union-target/index.php"
probe = "nonexistent-player' UNION SELECT 'union-ci-marker'-- -"
request = urllib.request.Request(
    url,
    data=urllib.parse.urlencode({"player": probe}).encode(),
    headers={"Content-Type": "application/x-www-form-urlencoded"},
)
with urllib.request.urlopen(request, timeout=10) as response:
    text = response.read().decode("utf-8", "replace")
assert "Sorry, union-ci-marker" in text, (
    "A real UNION result was not returned by the MariaDB-backed eligibility form"
)
print("PASS: normal HTTP POST reaches a genuine SQL UNION query, not a mock query evaluator")
