#!/usr/bin/env bash
# Executed inside the freshly bootstrapped image by build.sh.
set -euo pipefail
PAYLOAD=/tmp/attackbox-build
mapfile -t packages < <(sed 's/#.*//;s/^[[:space:]]*//;s/[[:space:]]*$//' "$PAYLOAD/packages.txt" | sed '/^$/d')
for package in "${packages[@]}"; do
  [[ $package =~ ^[a-z0-9][a-z0-9+.-]+$ ]] || { echo "Invalid package: $package" >&2; exit 1; }
done
printf 'wireshark-common wireshark-common/install-setuid boolean true\n' | debconf-set-selections
apt-get update -o Acquire::Retries=3
apt-get install -y --no-install-recommends -o Acquire::Retries=3 "${packages[@]}"
# parrot-core supplies the canonical Deb822 repository configuration. Keep it
# as the single source of repository settings after the bootstrap transaction.
test -s /etc/apt/sources.list.d/parrot.sources
rm /etc/apt/sources.list
apt-get check
audit="$(dpkg --audit)"
[[ -z "$audit" ]] || { printf '%s\n' "$audit" >&2; exit 1; }

# Let account tools enforce UID/GID uniqueness and maintain shadow/gshadow.
# Desktop defaults live in the system dconf database; each learner starts with
# a fresh user database rather than a precompiled copy that overrides them.
rm -f /etc/skel/.config/dconf/user
groupadd --gid 1013 box
useradd --uid 1001 --gid 1013 --create-home --shell /bin/bash box
usermod -a -G wireshark box
passwd -l root
passwd -l box
install -d -m 0755 /etc/sudoers.d
printf 'box ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/attackbox
chmod 0440 /etc/sudoers.d/attackbox
visudo -cf /etc/sudoers.d/attackbox

# Use the HTB settings shipped by parrot-core-htb as system-wide defaults.
install -D -m 0644 /usr/lib/parrot-skel/etc/dconf/db/local.d/htb-config /etc/dconf/db/local.d/htb-config
install -d /etc/dconf/profile
printf 'user-db:user\nsystem-db:local\n' > /etc/dconf/profile/user
cat > /etc/dconf/db/local.d/zz-attackbox <<'DCONF'
[org/mate/marco/general]
compositing-manager=false

[org/mate/interface]
enable-animations=false
DCONF
dconf update
printf 'en_US.UTF-8 UTF-8\nzh_CN.UTF-8 UTF-8\n' > /etc/locale.gen
locale-gen
printf 'LANG=en_US.UTF-8\n' > /etc/default/locale
printf 'attackbox\n' > /etc/hostname
printf '127.0.0.1 localhost\n127.0.1.1 attackbox\n::1 localhost ip6-localhost\n' > /etc/hosts

install -d /usr/share/attackbox
cp "$PAYLOAD/packages.txt" /usr/share/attackbox/packages.txt
dpkg-query -W -f='${binary:Package}\t${Version}\t${Installed-Size}\n' > /usr/share/attackbox/packages.tsv
printf '{"format":1,"uid":1001,"gid":1013}\n' > /etc/.attackbox_golden_ready
chmod 0444 /etc/.attackbox_golden_ready
apt-get clean
