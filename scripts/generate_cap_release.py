#!/usr/bin/env python3
"""Generate stable, versioned Cap user/root Flags and matching Challenge answers."""
from __future__ import annotations
import argparse, base64, json, re, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAG_DIR = ROOT / "labs/cap/flags"
RELEASE_DIR = FLAG_DIR / "releases"
USER_DOC = ROOT / "challenges/idor/cap-packet-drop/Packet-Drop.md"
ROOT_DOC = ROOT / "challenges/linux-privilege-escalation/cap-setuid/Setuid-Surprise.md"
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(?:-[a-z0-9]+(?:[.-][a-z0-9]+)*)?$")
FLAG_RE = re.compile(r"^TTP\\{[a-z2-7]{16}\\}$")

def new_flag():
    token = base64.b32encode(secrets.token_bytes(10)).decode("ascii").rstrip("=").lower()
    return f"TTP{{{token}}}"

def update_answer(path, values):
    text = path.read_text(encoding="utf-8")
    for value in values:
        text, count = re.subn(r'(?m)^answer: "TTP\\{[^"]+\\}"$', f'answer: "{value}"', text, count=1)
        if count != 1:
            raise SystemExit(f"expected one Flag answer slot for {path}, got {count}")
    path.write_text(text, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    version = parser.parse_args().version
    if not VERSION_RE.fullmatch(version):
        raise SystemExit("version must be numeric semver, e.g. 1.0.0")
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = RELEASE_DIR / f"{version}.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        flags = manifest.get("flags", {})
        if manifest.get("version") != version or set(flags) != {"user", "root"}:
            raise SystemExit("invalid existing Cap release manifest")
        if len(set(flags.values())) != 2 or not all(FLAG_RE.fullmatch(v) for v in flags.values()):
            raise SystemExit("Cap release manifest contains invalid/duplicate Flags")
        action = "reused"
    else:
        values = [new_flag(), new_flag()]
        while values[0] == values[1]:
            values[1] = new_flag()
        flags = {"user": values[0], "root": values[1]}
        manifest = {"version": version, "format": "TTP{16-lowercase-base32}", "flags": flags}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")
        action = "generated"

    FLAG_DIR.mkdir(parents=True, exist_ok=True)
    (FLAG_DIR / "user.txt").write_text(flags["user"] + "\\n", encoding="utf-8")
    (FLAG_DIR / "root.txt").write_text(flags["root"] + "\\n", encoding="utf-8")
    update_answer(USER_DOC, [flags["user"]])
    update_answer(ROOT_DOC, [flags["user"], flags["root"]])
    print(f"Cap release {version}: {action}; 2 unique random 80-bit Flags")
    print(f"Manifest: {manifest_path.relative_to(ROOT)}")
    print("Target Flag files and Challenge answers were synchronized; values are not printed.")

if __name__ == "__main__":
    main()
