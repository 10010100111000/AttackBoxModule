#!/usr/bin/env bash
# Offline image checks. Worker lifecycle acceptance is performed by the platform.
set -euo pipefail
[[ $# == 1 ]] || { echo 'Usage: check.sh ROOTFS' >&2; exit 1; }
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(realpath "$1")"
python3 "$SOURCE/desktop_check.py" static "$ROOT"
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
assert (root / 'usr/share/mate-panel/layouts/attackbox.layout').is_file()
assert (root / 'usr/share/applications/burpsuite.desktop').is_file()
assert (root / 'home/box/Desktop/chromium.desktop').is_file()
assert (root / 'home/box/Desktop/mate-terminal.desktop').is_file()
assert (root / 'home/box/.config/user-dirs.locale').read_text().strip() == 'en_US'
assert (root / 'home/box/Public').is_dir()
assert (root / 'usr/share/burpsuite/BurpSuiteCommunity').is_file()
assert (root / 'usr/share/burpsuite/.install4j/BurpSuiteCommunity.png').is_file()
assert (root / 'usr/local/bin/burpsuite').stat().st_mode & 0o111
assert (root / 'usr/share/attackbox/burp-ca.der').stat().st_size > 0
assert (root / 'home/box/.java/.userPrefs/burp/prefs.xml').stat().st_mode & 0o077 == 0
assert (root / 'home/box/.local/share/pki/nssdb/cert9.db').is_file()
policy = json.loads((root / 'etc/chromium/policies/managed/attackbox.json').read_text())
assert policy['BackgroundModeEnabled'] is False
assert len(policy['ExtensionInstallForcelist']) == 3
PY
source "$SOURCE/packages.sh"
declare -a required=() removed=()
inventory="$(chroot "$ROOT" /usr/bin/dpkg-query -W -f='${binary:Package}\t${db:Status-Status}\n')"
declare -A installed=()
while IFS=$'\t' read -r package status; do
  if [[ $status == installed ]]; then installed[${package%%:*}]=1; fi
done <<< "$inventory"
for list in packages desktop-packages; do
  read_packages "$ROOT/usr/share/attackbox/$list.txt" required
  for package in "${required[@]}"; do
    [[ ${installed[$package]:-} == 1 ]] || { echo "Required package missing: $package" >&2; exit 1; }
  done
done
read_packages "$ROOT/usr/share/attackbox/remove-packages.txt" removed
for package in "${removed[@]}"; do
  [[ ${installed[$package]:-} != 1 ]] || { echo "Removed package still installed: $package" >&2; exit 1; }
done
chroot "$ROOT" /usr/bin/env -i PATH=/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin /bin/bash -euc '
desktop-file-validate /usr/share/applications/burpsuite.desktop
for command in bash sudo nmap python3 Xtigervnc vncconfig mate-session mate-panel marco caja chromium dbus-run-session burpsuite msfconsole xfreerdp3 mate-screenshot mate-search-tool mate-calc eom engrampa geany xdg-open xdg-mime gio xclip desktop-file-validate; do
  command -v "$command" >/dev/null
done
for backend in /usr/libexec/gvfsd-sftp /usr/libexec/gvfsd-smb; do
  test -x "$backend"
done'
chroot "$ROOT" /usr/bin/python3 - settings < "$SOURCE/desktop_check.py"
for language in en_US.UTF-8 zh_CN.UTF-8; do
  chroot "$ROOT" /usr/bin/env -i PATH=/usr/bin:/bin LANG="$language" LC_ALL="$language" \
    python3 -c 'import locale; locale.setlocale(locale.LC_ALL, "")'
done
expected_caps="$(cat "$ROOT/usr/share/attackbox/file-capabilities.txt")"
actual_caps="$(chroot "$ROOT" /usr/bin/env LC_ALL=C /usr/sbin/getcap -r /usr | LC_ALL=C sort)"
[[ $expected_caps == "$actual_caps" ]] || { echo 'File capabilities differ from recorded image inventory' >&2; exit 1; }
chroot "$ROOT" /usr/sbin/runuser -u box -- certutil -L -d sql:/home/box/.local/share/pki/nssdb -n AttackBox-Burp > /dev/null
chroot "$ROOT" /usr/bin/nmap --version
chroot "$ROOT" /usr/bin/python3 --version
chroot "$ROOT" /usr/sbin/visudo -cf /etc/sudoers.d/attackbox
echo 'Golden image structure, package binaries and CLI checks passed'
