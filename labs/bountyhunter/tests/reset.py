#!/usr/bin/env python3
"""New container should have clean web state and recreate original forms."""
import urllib.request

for path, phrase in [
    ("/", b"BOUNTY HUNTERS"),
    ("/portal.php", b"Portal under development."),
    ("/log_submit.php", b"Bounty Report System - Beta"),
]:
    with urllib.request.urlopen("http://bountyhunter-target" + path, timeout=8) as response:
        assert phrase in response.read()
print("PASS: fresh BountyHunter instance restores portal and tracker state", flush=True)
