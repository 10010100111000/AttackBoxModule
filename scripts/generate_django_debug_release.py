#!/usr/bin/env python3
"""Generate a version-pinned random Flag shared by Django Lab and Challenge."""
from __future__ import annotations

import argparse
import base64
import json
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAG_FILE = ROOT / "labs/django-debug-xss/flags/user.txt"
MANIFEST_DIR = ROOT / "labs/django-debug-xss/flags/releases"
CHALLENGE = ROOT / "challenges/xss/harbor-registry/Harbor-Lights.md"
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[a-z0-9]+(?:[.-][a-z0-9]+)*)?$")
FLAG_RE = re.compile(r"^TTP\{[a-z2-7]{16}\}$")


def new_flag() -> str:
    token = base64.b32encode(secrets.token_bytes(10)).decode("ascii").rstrip("=").lower()
    return f"TTP{{{token}}}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    version = parser.parse_args().version
    if not VERSION_RE.fullmatch(version):
        raise SystemExit("version must be numeric semver, e.g. 1.0.0")

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFEST_DIR / f"{version}.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        flag = manifest.get("flag")
        if manifest.get("version") != version or not isinstance(flag, str) or not FLAG_RE.fullmatch(flag):
            raise SystemExit("existing release manifest is invalid")
        action = "reused"
    else:
        flag = new_flag()
        manifest = {
            "version": version,
            "format": "TTP{16-lowercase-base32}",
            "flag": flag,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        action = "generated"

    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAG_FILE.write_text(flag + "\n", encoding="utf-8")

    text = CHALLENGE.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'(?m)^answer:\s*"TTP\{[a-z2-7]{16}\}"$',
        f'answer: "{flag}"',
        text,
    )
    if count != 1:
        raise SystemExit(f"expected exactly one Flag answer in {CHALLENGE}, found {count}")
    CHALLENGE.write_text(updated, encoding="utf-8")

    print(f"Django Debug XSS release {version}: {action}; one random 80-bit Flag")
    print(f"Manifest: {manifest_path.relative_to(ROOT)}")
    print("靶机 Flag 与 Challenge 答案已从同一 Manifest 同步；不输出 Flag 值。")


if __name__ == "__main__":
    main()
