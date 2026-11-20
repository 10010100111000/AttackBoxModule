#!/usr/bin/env bash
# Executed inside the freshly bootstrapped image by build.sh.
set -euo pipefail
PAYLOAD=/tmp/attackbox-build
[[ -r "$PAYLOAD/packages.txt" && -d "$PAYLOAD/skel" && -r "$PAYLOAD/chromium-policy.json" && -r "$PAYLOAD/mate-defaults.ini" ]] || {
  echo 'Run this script through golden/build.sh inside the build rootfs' >&2
  exit 1
}
mapfile -t packages < <(sed 's/#.*//;s/^[[:space:]]*//;s/[[:space:]]*$//' "$PAYLOAD/packages.txt" | sed '/^$/d')
for package in "${packages[@]}"; do
  [[ $package =~ ^[a-z0-9][a-z0-9+.-]+$ ]] || { echo "Invalid package: $package" >&2; exit 1; }
done
printf 'wireshark-common wireshark-common/install-setuid boolean true\n' | debconf-set-selections
apt-get update -o Acquire::Retries=3 -o APT::Update::Error-Mode=any
apt-get install -y --no-install-recommends -o Acquire::Retries=3 "${packages[@]}"
# parrot-core supplies the canonical Deb822 repository configuration. Keep it
# as the single source of repository settings after the bootstrap transaction.
test -s /etc/apt/sources.list.d/parrot.sources
rm /etc/apt/sources.list
# Upgrade the base packages as well as explicitly requested applications.
apt-get full-upgrade -y --no-install-recommends -o Acquire::Retries=3
apt-get check
audit="$(dpkg --audit)"
[[ -z "$audit" ]] || { printf '%s\n' "$audit" >&2; exit 1; }

# Let account tools enforce UID/GID uniqueness and maintain shadow/gshadow.
# Desktop defaults live in the system dconf database; each learner starts with
# a fresh user database rather than a precompiled copy that overrides them.
# Parrot ships a complete workstation profile, including optional applets.
# New learner homes use this project's small, explicit skeleton instead.
find /etc/skel /root -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cp -a "$PAYLOAD/skel/." /etc/skel/
cp -a "$PAYLOAD/skel/." /root/
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
install -m 0644 "$PAYLOAD/mate-defaults.ini" /etc/dconf/db/local.d/zz-attackbox
dconf update
printf 'en_US.UTF-8 UTF-8\nzh_CN.UTF-8 UTF-8\n' > /etc/locale.gen
locale-gen
# Fail the build if the requested locales were not actually generated.
for language in en_US.UTF-8 zh_CN.UTF-8; do
  env -i PATH=/usr/bin:/bin LANG="$language" LC_ALL="$language" \
    python3 -c 'import locale; locale.setlocale(locale.LC_ALL, "")'
done
printf 'LANG=en_US.UTF-8\n' > /etc/default/locale
python3 "$PAYLOAD/desktop_defaults.py" /home/box /usr/share/applications
install -D -m 0644 "$PAYLOAD/chromium-policy.json" /etc/chromium/policies/managed/attackbox.json
cat > /home/box/.config/mimeapps.list <<'MIME'
[Default Applications]
x-scheme-handler/http=chromium.desktop
x-scheme-handler/https=chromium.desktop
text/html=chromium.desktop
MIME
chown -R 1001:1013 /home/box/.config
if [[ -d /home/box/.local ]]; then chown -R 1001:1013 /home/box/.local; fi
printf 'attackbox\n' > /etc/hostname
printf '127.0.0.1 localhost\n127.0.1.1 attackbox\n::1 localhost ip6-localhost\n' > /etc/hosts

install -D -m 0755 "$PAYLOAD/bin/burpsuite" /usr/local/bin/burpsuite
install -D -m 0644 "$PAYLOAD/applications/attackbox-burpsuite.desktop" /usr/share/applications/attackbox-burpsuite.desktop

install -d /usr/share/attackbox
install -m 0644 "$PAYLOAD/burp-user-config.json" /usr/share/attackbox/burp-user-config.json
# The repository owner authorizes accepting Burp Community terms during CI.
runuser -u box -- /usr/bin/env HOME=/home/box LANG=en_US.UTF-8 \
  python3 "$PAYLOAD/burp_ca.py" initialize
install -m 0644 /home/box/.local/share/attackbox/burp-ca.der /usr/share/attackbox/burp-ca.der
# Current Chromium uses the XDG data directory for its NSS certificate database.
install -d -m 0700 -o 1001 -g 1013 /home/box/.local/share/pki/nssdb
runuser -u box -- certutil -N -d sql:/home/box/.local/share/pki/nssdb --empty-password
runuser -u box -- certutil -A -d sql:/home/box/.local/share/pki/nssdb \
  -n AttackBox-Burp -t 'C,,' -i /usr/share/attackbox/burp-ca.der
cp "$PAYLOAD/packages.txt" /usr/share/attackbox/
LC_ALL=C getcap -r /usr | LC_ALL=C sort > /usr/share/attackbox/file-capabilities.txt
dpkg-query -W -f='${binary:Package}\t${Version}\t${Installed-Size}\n' > /usr/share/attackbox/packages.tsv
printf '{"format":1,"uid":1001,"gid":1013}\n' > /etc/.attackbox_golden_ready
chmod 0444 /etc/.attackbox_golden_ready
apt-get clean
