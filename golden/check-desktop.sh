#!/usr/bin/env bash
# Exercise the desktop on a disposable snapshot; never persist test profiles.
set -euo pipefail
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ${1:-} == --session ]]; then
  [[ $(id -u) == 1001 ]] || { echo 'Desktop must run as box' >&2; exit 1; }
  stage='VNC startup'
  result=0
  trap 'result=$?; printf "Desktop acceptance failed at %s (exit %s): %s\n" "$stage" "$result" "$BASH_COMMAND" >&2; python3 /tmp/desktop_check.py snapshot /var/log/attackbox-check/state.json || true; exit "$result"' ERR
  export DISPLAY=:99 XDG_RUNTIME_DIR=/tmp/runtime-box XDG_CURRENT_DESKTOP=MATE XDG_SESSION_TYPE=x11
  Xtigervnc :99 -rfbunixpath /run/attackbox/gui.sock -rfbunixmode 0600 \
    -rfbport -1 -nolisten tcp -SecurityTypes None -AlwaysShared \
    -geometry 1280x800 -depth 24 > /var/log/attackbox-check/vnc.log 2>&1 &
  vnc=$!
  for ((i=0; i<100; i++)); do
    kill -0 "$vnc"
    [[ -S /tmp/.X11-unix/X99 && -S /run/attackbox/gui.sock ]] && break
    sleep 0.1
  done
  [[ -S /tmp/.X11-unix/X99 && -S /run/attackbox/gui.sock ]]
  vncconfig -nowin > /var/log/attackbox-check/vncconfig.log 2>&1 &
  mate-session > /var/log/attackbox-check/mate.log 2>&1 &
  python3 /tmp/desktop_check.py watch /var/log/attackbox-check/windows.done > /var/log/attackbox-check/windows.log 2>&1 &
  window_check=$!
  stage='Chromium and Burp HTTPS'
  python3 /tmp/burp_ca.py verify-browser
  stage='desktop operations'
  python3 /tmp/desktop_smoke.py
  touch /var/log/attackbox-check/windows.done
  stage='startup dialogs'
  wait "$window_check"
  head -n 1 /var/log/attackbox-check/windows.log
  stage='VNC protocol'
  python3 - <<'PY_SOCKET'
import socket
with socket.socket(socket.AF_UNIX) as connection:
    connection.settimeout(5)
    connection.connect('/run/attackbox/gui.sock')
    with connection.makefile('rb') as stream:
        greeting = stream.read(12)
    assert len(greeting) == 12 and greeting.startswith(b'RFB '), greeting
PY_SOCKET
  stage='desktop process liveness'
  pgrep -u box -x mate-session
  pgrep -u box -x mate-panel
  pgrep -u box -x marco
  pgrep -u box -x vncconfig
  exit 0
fi

if [[ ${1:-} == --inside ]]; then
  ROOT=$2
  source "$SOURCE/mounts.sh"
  mount_rootfs "$ROOT"
  chroot "$ROOT" /usr/bin/dbus-uuidgen > "$ROOT/etc/machine-id"
  cp "$ROOT/etc/machine-id" "$ROOT/var/lib/dbus/machine-id"
  mount_image -t tmpfs -o nosuid,nodev,mode=1777 tmpfs "$ROOT/tmp"
  install -d -m 1777 "$ROOT/tmp/.ICE-unix" "$ROOT/tmp/.X11-unix"
  install -d -m 0700 -o 1001 -g 1013 "$ROOT/run/attackbox" "$ROOT/tmp/runtime-box" "$ROOT/var/log/attackbox-check"
  install -m 0755 "$0" "$ROOT/tmp/check-desktop.sh"
  install -m 0644 "$SOURCE/burp_ca.py" "$SOURCE/desktop_check.py" "$SOURCE/desktop_defaults.py" "$SOURCE/desktop_smoke.py" "$ROOT/tmp/"
  # A private PID namespace guarantees all browser/desktop children are reaped
  # on exit, including D-Bus services that outlive their launching shell.
  chroot "$ROOT" /usr/sbin/runuser -u box -- /usr/bin/env -i \
    HOME=/home/box USER=box LOGNAME=box PATH=/usr/local/bin:/usr/bin:/bin \
    LANG=en_US.UTF-8 DISPLAY=:99 XDG_RUNTIME_DIR=/tmp/runtime-box \
    XDG_CURRENT_DESKTOP=MATE XDG_SESSION_TYPE=x11 /usr/bin/dbus-run-session /bin/bash /tmp/check-desktop.sh --session
  exit 0
fi

[[ $EUID == 0 && $# == 1 ]] || { echo 'Usage: sudo check-desktop.sh READ_ONLY_GOLDEN' >&2; exit 1; }
ROOT="$(realpath "$1")"
[[ $(btrfs property get "$ROOT" ro) == ro=true ]] || { echo 'Expected a read-only golden subvolume' >&2; exit 1; }
WORK="$(mktemp -d "$(dirname "$ROOT")/.desktop-check.XXXXXX")"
CREATED=0
cleanup() {
  local code=$?
  if ((CREATED)); then btrfs subvolume delete "$WORK/rootfs" || code=1; fi
  rmdir "$WORK" || code=1
  exit "$code"
}
trap cleanup EXIT
btrfs subvolume snapshot "$ROOT" "$WORK/rootfs"
CREATED=1
set +e
timeout --signal=TERM --kill-after=10 300 \
  unshare --mount --pid --fork --kill-child --propagation private \
  /bin/bash "$0" --inside "$WORK/rootfs"
RESULT=$?
set -e
if ((RESULT != 0)); then
  for logfile in vnc.log vncconfig.log mate.log chromium.log windows.log state.json; do
    file="$WORK/rootfs/var/log/attackbox-check/$logfile"
    if [[ -f $file ]]; then
      printf '::group::Desktop diagnostic: %s\n' "$logfile"
      tail -n 100 "$file"
      printf '::endgroup::\n'
    fi
  done
  exit "$RESULT"
fi
echo 'Disposable desktop acceptance passed; golden remains unchanged'
