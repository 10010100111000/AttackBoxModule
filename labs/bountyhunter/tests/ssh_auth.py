#!/usr/bin/env python3
"""Confirm that the independent SSH server accepts the development account."""
import os
import subprocess

password = os.environ["BOUNTY_TEST_PASSWORD"]
assert password
result = subprocess.run(
    [
        "sshpass", "-p", password, "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "PreferredAuthentications=password",
        "-o", "PubkeyAuthentication=no",
        "-o", "ConnectTimeout=6",
        "development@bountyhunter-target",
        "id -un; test -r /home/development/user.txt; test ! -r /root/root.txt",
    ],
    capture_output=True, text=True, timeout=14, check=True,
)
assert result.stdout.strip() == "development", result.stdout
print("PASS: normal password authentication grants the development account, not root", flush=True)
