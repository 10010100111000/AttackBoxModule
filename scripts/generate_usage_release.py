#!/usr/bin/env python3
"""Generate one deterministic-per-version Usage Flag set and synchronize image seeds/Challenges."""
from __future__ import annotations

import argparse
import base64
import json
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "labs/usage"
FLAG_DIR = LAB / "flags"
MANIFEST_DIR = FLAG_DIR / "releases"
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(?:-[a-z0-9]+(?:[.-][a-z0-9]+)*)?$")
FLAG_RE = re.compile(r"^TTP\\{[a-z2-7]{16}\\}$")
CHALLENGES = {
    "database": (ROOT / "challenges/sql-injection/11-usage/blind-recovery.md", 1),
    "user": (ROOT / "challenges/startpoint/usage/Usage.md", 1),
    "root": (ROOT / "challenges/startpoint/usage/Usage.md", 2),
    "upload": (ROOT / "challenges/file-security/usage/admin-avatar-upload.md", 1),
    "archive": (ROOT / "challenges/linux-privilege-escalation/usage/7za-listfile.md", 1),
}


def new_flag() -> str:
    token = base64.b32encode(secrets.token_bytes(10)).decode("ascii").rstrip("=").lower()
    return f"TTP{{{token}}}"


def validate_flags(flags: dict[str, str]) -> None:
    if set(flags) != {"database", "user", "root"}:
        raise SystemExit("Usage manifest must contain database, user and root Flags")
    if any(not isinstance(value, str) or not FLAG_RE.fullmatch(value) for value in flags.values()):
        raise SystemExit("Usage manifest contains an invalid Flag")
    if len(set(flags.values())) != 3:
        raise SystemExit("Usage release Flags must be distinct")


def sync_answers(path: Path, values: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if "lab: usage" not in text:
        raise SystemExit(f"{path.relative_to(ROOT)} is not bound to Usage")
    answer_re = re.compile(r'(?m)^answer: "([^"]+)"$')
    matches = list(answer_re.finditer(text))
    if len(matches) != len(values):
        raise SystemExit(
            f"{path.relative_to(ROOT)}: expected {len(values)} Flag answers, found {len(matches)}"
        )
    for match, value in reversed(list(zip(matches, values))):
        text = text[:match.start()] + f'answer: "{value}"' + text[match.end():]
    path.write_text(text, encoding="utf-8")


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
            raise SystemExit("Usage release manifest version mismatch")
        flags = manifest.get("flags")
        if not isinstance(flags, dict):
            raise SystemExit("Usage release manifest is missing its flags object")
        validate_flags(flags)
        action = "reused"
    else:
        flags = {"database": new_flag(), "user": new_flag(), "root": new_flag()}
        while len(set(flags.values())) != 3:
            flags = {"database": new_flag(), "user": new_flag(), "root": new_flag()}
        manifest = {
            "version": version,
            "format": "TTP{16-lowercase-base32}",
            "flags": flags,
        }
        validate_flags(flags)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")
        action = "generated"

    FLAG_DIR.mkdir(parents=True, exist_ok=True)
    for name, value in flags.items():
        (FLAG_DIR / f"{name}.txt").write_text(value + "\\n", encoding="utf-8")

    sync_answers(CHALLENGES["database"][0], [flags["database"]])
    sync_answers(CHALLENGES["user"][0], [flags["user"], flags["root"]])
    sync_answers(CHALLENGES["upload"][0], [flags["user"]])
    sync_answers(CHALLENGES["archive"][0], [flags["root"]])

    print(f"Usage release {version}: {action}; three target seeds and four Challenge files synchronized")
    print("Flag values are intentionally not printed.")


if __name__ == "__main__":
    main()
