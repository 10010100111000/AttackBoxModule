#!/usr/bin/env python3
"""Generate a stable, versioned random Devvortex Web Flag and Challenge answer."""
from __future__ import annotations
import argparse, base64, json, re, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAG_FILE = ROOT / "labs/devvortex/flags/user.txt"
MANIFEST_DIR = ROOT / "labs/devvortex/flags/releases"
CHALLENGE = ROOT / "challenges/startpoint/devvortex/Devvortex.md"
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(?:-[a-z0-9]+(?:[.-][a-z0-9]+)*)?$")
FLAG_RE = re.compile(r"^TTP\\{[a-z2-7]{16}\\}$")
ANSWER_RE = re.compile(r'(?m)^answer: "TTP\\{[^"]+\\}"$')

def new_flag():
    token = base64.b32encode(secrets.token_bytes(10)).decode("ascii").rstrip("=").lower()
    return f"TTP{{{token}}}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    version = parser.parse_args().version
    if not VERSION_RE.fullmatch(version):
        raise SystemExit("version must be numeric semver, e.g. 0.1.0")
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFEST_DIR / f"{version}.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        flag = manifest.get("flag")
        if manifest.get("version") != version or not isinstance(flag, str) or not FLAG_RE.fullmatch(flag):
            raise SystemExit("existing Devvortex release manifest is invalid")
        action = "reused"
    else:
        flag = new_flag()
        manifest = {"version": version, "format": "TTP{16-lowercase-base32}", "flag": flag}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n")
        action = "generated"
    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAG_FILE.write_text(flag + "\\n")
    challenge = CHALLENGE.read_text()
    updated, count = ANSWER_RE.subn(f'answer: "{flag}"', challenge)
    if count != 1:
        raise SystemExit(f"expected exactly one Flag answer, found {count}")
    CHALLENGE.write_text(updated)
    print(f"Devvortex release {version}: {action}; target seed and Challenge answer synchronized")

if __name__ == "__main__":
    main()
