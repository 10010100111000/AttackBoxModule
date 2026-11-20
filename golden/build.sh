#!/usr/bin/env bash
# Adapted from Parrot's debootstrap recipe, revision recorded in README.md.
set -euo pipefail
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ $EUID == 0 ]] || { echo 'Run as root' >&2; exit 1; }
if [[ ${ATTACKBOX_GOLDEN_NAMESPACE:-} != 1 ]]; then
  exec unshare --mount --propagation private env ATTACKBOX_GOLDEN_NAMESPACE=1 bash "$0" "$@"
fi
[[ $# == 2 && $1 == --target && -n $2 ]] || { echo 'Usage: build.sh --target BTRFS_SUBVOLUME' >&2; exit 1; }
TARGET="$(realpath -m "$2")"
[[ ! -e "$TARGET" && ! -L "$TARGET" ]] || { echo 'Target already exists' >&2; exit 1; }
mkdir -p "$(dirname "$TARGET")"
[[ $(stat -f -c %T "$(dirname "$TARGET")") == btrfs ]] || { echo 'Target must reside on Btrfs' >&2; exit 1; }
source "$SOURCE/mounts.sh"
CACHE="$(mktemp -d)"
CREATED=0
SUCCESS=0
cleanup() {
  local code=$? safe=1
  unmount_image || { safe=0; code=1; echo 'Unmount failed; image retained for inspection' >&2; }
  if ((safe && CREATED && !SUCCESS)); then
    btrfs subvolume delete "$TARGET" || code=1
  fi
  rm -rf -- "$CACHE"
  exit "$code"
}
trap cleanup EXIT

# This keyring authenticates debootstrap's Release metadata and all APT packages.
curl --fail --location --retry 3 --max-time 120 \
  https://deb.parrot.sh/parrot/misc/parrotsec.gpg -o "$CACHE/parrot.asc"
printf '%s  %s\n' 8b7d58471a91e03f9e62d9f07d13304be7b84f288c1ca7d548ffaf5f27ad35f4 "$CACHE/parrot.asc" | sha256sum -c -
gpg --homedir "$CACHE" --batch --dearmor --output "$CACHE/parrot.gpg" "$CACHE/parrot.asc"
btrfs subvolume create "$TARGET"
CREATED=1
# Ubuntu's debootstrap has no echo alias. Use its standard Debian suite script
# explicitly, with Parrot's suite, mirror and authenticated archive keyring.
debootstrap --arch=amd64 --variant=minbase --merged-usr \
  --components=main,contrib,non-free,non-free-firmware \
  --include=gnupg,ca-certificates,parrot-archive-keyring --exclude=parrot-core \
  --keyring="$CACHE/parrot.gpg" echo "$TARGET" https://deb.parrot.sh/parrot \
  /usr/share/debootstrap/scripts/sid

cat > "$TARGET/etc/apt/sources.list" <<'APT'
deb [signed-by=/usr/share/keyrings/parrot-archive-keyring.gpg] https://deb.parrot.sh/parrot echo main contrib non-free non-free-firmware
deb [signed-by=/usr/share/keyrings/parrot-archive-keyring.gpg] https://deb.parrot.sh/parrot echo-security main contrib non-free non-free-firmware
deb [signed-by=/usr/share/keyrings/parrot-archive-keyring.gpg] https://deb.parrot.sh/parrot echo-backports main contrib non-free non-free-firmware
APT
rm -f "$TARGET/etc/resolv.conf"
printf 'nameserver 1.1.1.1\nnameserver 8.8.8.8\n' > "$TARGET/etc/resolv.conf"
printf '#!/bin/sh\nexit 101\n' > "$TARGET/usr/sbin/policy-rc.d"
chmod 0755 "$TARGET/usr/sbin/policy-rc.d"
install -d "$TARGET/tmp/attackbox-build" "$TARGET/proc" "$TARGET/sys" "$TARGET/dev" "$TARGET/run"
install -m 0644 "$SOURCE/packages.txt" "$SOURCE/configure.sh" "$SOURCE/desktop_defaults.py" "$SOURCE/desktop_check.py" "$SOURCE/chromium-policy.json" "$SOURCE/mate-defaults.ini" "$SOURCE/attackbox.layout" "$SOURCE/burp_ca.py" "$SOURCE/burp-user-config.json" "$TARGET/tmp/attackbox-build/"

cp -a "$SOURCE/skel" "$SOURCE/bin" "$SOURCE/applications" "$TARGET/tmp/attackbox-build/"

mount_rootfs "$TARGET"
chroot "$TARGET" /usr/bin/env -i HOME=/root PATH=/usr/sbin:/usr/bin:/sbin:/bin \
  LANG=C.UTF-8 LC_ALL=C.UTF-8 DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC \
  /bin/bash /tmp/attackbox-build/configure.sh
unmount_image
rm "$TARGET/usr/sbin/policy-rc.d"
for directory in boot usr/lib/modules usr/lib/firmware tmp var/tmp run var/log var/lib/apt/lists var/cache/apt/archives; do
  mkdir -p "$TARGET/$directory"
  find "$TARGET/$directory" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
done
chmod 1777 "$TARGET/tmp" "$TARGET/var/tmp"
rm -f "$TARGET/etc/machine-id" "$TARGET/var/lib/dbus/machine-id"
touch "$TARGET/etc/machine-id"
mkdir -p "$TARGET/var/lib/dbus"
touch "$TARGET/var/lib/dbus/machine-id"
rm -f "$TARGET/etc/ssh/ssh_host_"* "$TARGET/root/.bash_history" \
  "$TARGET/etc/passwd-" "$TARGET/etc/group-" "$TARGET/etc/shadow-" "$TARGET/etc/gshadow-"
btrfs property set "$TARGET" ro true
SUCCESS=1
echo "Golden rootfs ready: $TARGET"
