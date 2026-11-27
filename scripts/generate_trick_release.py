#!/usr/bin/env python3
"""Generate a stable versioned User/Root Flag pair for the Trick Lab."""
from __future__ import annotations
import argparse
import base64
import json
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "labs/trick/flags/releases"
CHALLENGE = ROOT / "challenges/integrated/trick/Trick.md"
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[a-z0-9]+(?:[.-][a-z0-9]+)*)?$")
FLAG_RE = re.compile(r"^TTP\{[a-z2-7]{16}\}$")
ANSWER_RE = re.compile(r'(?m)^(answer:\s*)"[^"]+"$')


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
            raise SystemExit("existing Trick release manifest is invalid")
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

    challenge = CHALLENGE.read_text(encoding="utf-8")
    answers = iter((user_flag, root_flag))
    updated, count = ANSWER_RE.subn(lambda match: f'{match.group(1)}"{next(answers)}"', challenge)
    if count != 2:
        raise SystemExit(f"expected exactly two Trick Flag answers, found {count}")
    CHALLENGE.write_text(updated, encoding="utf-8")
    print(f"Trick release {version}: {action}; User/Root Flag manifest and Challenge answers synchronized")


if __name__ == "__main__":
    main()
