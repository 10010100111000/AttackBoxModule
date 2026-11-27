#!/usr/bin/env python3
"""Generate stable versioned random User/Root Flags for the Base Lab."""
from __future__ import annotations

import argparse
import base64
import json
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_FLAG = ROOT / "labs/base/user_flag.txt"
ROOT_FLAG = ROOT / "labs/base/root_flag.txt"
MANIFEST_DIR = ROOT / "labs/base/flags/releases"
CHALLENGE = ROOT / "challenges/startpoint/base/Base.md"
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[a-z0-9]+(?:[.-][a-z0-9]+)*)?$")
FLAG_RE = re.compile(r"^TTP\{[a-z2-7]{16}\}$")
USER_ANSWER = re.compile(r'(?m)^(answer:\s*)"[^"]+"(?=\nmatch: trim\nhint:.*蛛丝马迹)')
ROOT_ANSWER = re.compile(r'(?m)^(answer:\s*)"[^"]+"(?=\nmatch: trim\nhint:.*特殊管理指令)')


def new_flag() -> str:
    token = base64.b32encode(secrets.token_bytes(10)).decode("ascii").rstrip("=").lower()
    return f"TTP{{{token}}}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    version = parser.parse_args().version
    if not VERSION_RE.fullmatch(version):
        raise SystemExit("version must be numeric semver, e.g. 0.1.0")

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFEST_DIR / f"{version}.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        user_flag, root_flag = manifest.get("user_flag"), manifest.get("root_flag")
        if manifest.get("version") != version or not all(
            isinstance(value, str) and FLAG_RE.fullmatch(value)
            for value in (user_flag, root_flag)
        ) or user_flag == root_flag:
            raise SystemExit("existing Base release manifest is invalid")
        action = "reused"
    else:
        user_flag, root_flag = new_flag(), new_flag()
        while root_flag == user_flag:
            root_flag = new_flag()
        manifest = {
            "version": version,
            "format": "TTP{16-lowercase-base32}",
            "user_flag": user_flag,
            "root_flag": root_flag,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        action = "generated"

    USER_FLAG.write_text(user_flag + "\n", encoding="utf-8")
    ROOT_FLAG.write_text(root_flag + "\n", encoding="utf-8")
    challenge = CHALLENGE.read_text(encoding="utf-8")
    challenge, user_count = USER_ANSWER.subn(lambda match: f'{match.group(1)}"{user_flag}"', challenge, count=1)
    challenge, root_count = ROOT_ANSWER.subn(lambda match: f'{match.group(1)}"{root_flag}"', challenge, count=1)
    if user_count != 1 or root_count != 1:
        raise SystemExit(f"expected one User and one Root Flag answer; got user={user_count}, root={root_count}")
    CHALLENGE.write_text(challenge, encoding="utf-8")
    print(f"Base release {version}: {action}; User/Root seeds, manifest and Challenge answers synchronized")


if __name__ == "__main__":
    main()
