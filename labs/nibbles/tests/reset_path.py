#!/usr/bin/env python3
import os
import urllib.error
import urllib.request
base = os.environ.get("TARGET_URL", "http://nibbles-target")
def fetch(path):
    try:
        with urllib.request.urlopen(base+path, timeout=10) as x:
            return x.status, x.read().decode(errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(errors="replace")
status, home = fetch("/")
assert status == 200 and "Hello world!" in home
status, readme = fetch("/nibbleblog/README")
assert status == 200 and "Version: v4.0.3" in readme
status, output = fetch("/nibbleblog/content/private/plugins/my_image/image.php")
assert status == 404, f"Upload persisted into a recreated instance: {status}"
print("PASS: fresh container restored unexploited Nibbleblog state")
