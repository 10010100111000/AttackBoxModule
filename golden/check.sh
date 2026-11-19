#!/usr/bin/env bash
# Offline image checks. Worker lifecycle acceptance is performed by the platform.
set -euo pipefail
[[ $# == 1 ]] || { echo 'Usage: check.sh ROOTFS' >&2; exit 1; }
ROOT="$(realpath "$1")"
[[ $(btrfs property get "$ROOT" ro) == ro=true ]] || { echo 'Golden must be read-only' >&2; exit 1; }
python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
assert json.loads((root / 'etc/.attackbox_golden_ready').read_text()) == {'format': 1, 'uid': 1001, 'gid': 1013}
assert 'box:x:1001:1013:' in (root / 'etc/passwd').read_text()
assert not (root / 'etc/resolv.conf').is_symlink()
for name in ['etc/machine-id', 'var/lib/dbus/machine-id']:
    assert (root / name).read_text() == '', name
for directory in ['boot', 'usr/lib/modules', 'usr/lib/firmware']:
    assert not any((root / directory).iterdir()), directory
assert (root / 'usr/share/mate-panel/layouts/default.layout').is_file()
PY
chroot "$ROOT" /usr/bin/env -i PATH=/usr/sbin:/usr/bin:/sbin:/bin /bin/bash -euc '
for command in bash sudo nmap python3 Xtigervnc mate-session mate-panel marco caja firefox-esr dbus-run-session burpsuite caido msfconsole; do
  command -v "$command" >/dev/null
done'
chroot "$ROOT" /usr/bin/nmap --version
chroot "$ROOT" /usr/bin/python3 --version
chroot "$ROOT" /usr/sbin/visudo -cf /etc/sudoers.d/attackbox
echo 'Golden image structure, package binaries and CLI checks passed'
