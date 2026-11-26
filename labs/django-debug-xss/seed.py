#!/usr/bin/env python3
"""Create per-instance Django sessions secret, private editorial account and Flag."""
import os
import json
import secrets
import pwd
from pathlib import Path

lab = pwd.getpwnam("lab")
bot = pwd.getpwnam("reviewbot")
root = Path("/run/django")
root.mkdir(parents=True, exist_ok=True)

password = os.environ.get("DJANGO_EDITOR_PASSWORD") or secrets.token_urlsafe(32)
flag = os.environ.get("DJANGO_XSS_FLAG") or (Path("/app/flags/user.txt")).read_text(encoding="utf-8").strip()
if len(password) < 12 or not flag.startswith("TTP{") or len(flag) > 256:
    raise SystemExit("Invalid instance editorial credentials or Flag")

def write_secret(name, content, owner):
    path = root / name
    path.write_text(content, encoding="utf-8")
    os.chown(path, owner.pw_uid, owner.pw_gid)
    path.chmod(0o600)

write_secret("admin-password", password, lab)
write_secret("django-secret", secrets.token_urlsafe(48), lab)
write_secret("editorial.flag", flag + "\n", lab)
write_secret("reviewbot.json", json.dumps({"password": password}), bot)
print("Django editorial instance initialized", flush=True)
