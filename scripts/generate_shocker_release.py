#!/usr/bin/env python3
"""Generate a versioned Shocker User/Root Flag pair and synchronize all Challenge answers."""
from __future__ import annotations

import argparse
import base64
import json
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAG_DIR = ROOT / "labs/shocker/flags"
MANIFEST_DIR = FLAG_DIR / "releases"
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[a-z0-9]+(?:[.-][a-z0-9]+)*)?$")
FLAG_RE = re.compile(r"^TTP\{[a-z2-7]{16}\}$")
CHALLENGES = {
    "integrated": (ROOT / "challenges/startpoint/shocker/Shocker.md", ["user", "root"]),
    "shellshock": (ROOT / "challenges/command-injection/shocker/cgi-shellshock.md", ["user"]),
    "sudo": (ROOT / "challenges/linux-privilege-escalation/shocker/sudo-perl.md", ["root"]),
}


def new_flag() -> str:
    token = base64.b32encode(secrets.token_bytes(10)).decode("ascii").rstrip("=").lower()
    return f"TTP{{{token}}}"


def validate_flags(flags: dict[str, str]) -> None:
    if set(flags) != {"user", "root"}:
        raise SystemExit("Shocker manifest must contain User and Root Flags")
    if any(not isinstance(value, str) or not FLAG_RE.fullmatch(value) for value in flags.values()):
        raise SystemExit("Shocker manifest contains an invalid Flag")
    if len(set(flags.values())) != 2:
        raise SystemExit("Shocker User and Root Flags must be distinct")


def sync_answers(path: Path, values: list[str]) -> None:
    content = path.read_text(encoding="utf-8")
    if not re.search(r"(?m)^lab: shocker$", content):
        raise SystemExit(f"{path.relative_to(ROOT)} is not bound to Shocker")
    answer_re = re.compile(r'(?m)^answer: "([^"]+)"$')
    matches = list(answer_re.finditer(content))
    if len(matches) != len(values):
        raise SystemExit(f"{path.relative_to(ROOT)}: expected {len(values)} Flag answers, found {len(matches)}")
    for match, value in reversed(list(zip(matches, values))):
        content = content[:match.start()] + f'answer: "{value}"' + content[match.end():]
    path.write_text(content, encoding="utf-8")


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
        if manifest.get("version") != version:
            raise SystemExit("Shocker release manifest version mismatch")
        flags = manifest.get("flags")
        if not isinstance(flags, dict):
            raise SystemExit("Shocker release manifest is missing its flags object")
        validate_flags(flags)
        action = "reused"
    else:
        flags = {"user": new_flag(), "root": new_flag()}
        while flags["user"] == flags["root"]:
            flags["root"] = new_flag()
        manifest = {
            "version": version,
            "format": "TTP{16-lowercase-base32}",
            "flags": flags,
        }
        validate_flags(flags)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        action = "generated"

    FLAG_DIR.mkdir(parents=True, exist_ok=True)
    for name, value in flags.items():
        (FLAG_DIR / f"{name}.txt").write_text(value + "\n", encoding="utf-8")

    for challenge_name, (path, names) in CHALLENGES.items():
        sync_answers(path, [flags[name] for name in names])

    print(f"Shocker release {version}: {action}; image seeds and three Challenge answer files synchronized")
    print("Flag values are intentionally not printed.")


if __name__ == "__main__":
    main()
