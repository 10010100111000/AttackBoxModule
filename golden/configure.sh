#!/usr/bin/env bash
# Executed inside the freshly bootstrapped image by build.sh.
set -euo pipefail
PAYLOAD=/tmp/attackbox-build
[[ -r "$PAYLOAD/packages.txt" && -r "$PAYLOAD/chromium-policy.json" && -r "$PAYLOAD/mate-defaults.ini" && -r "$PAYLOAD/attackbox.layout" ]] || {
  echo 'Run this script through golden/build.sh inside the build rootfs' >&2
  exit 1
}
# Let account tools enforce UID/GID uniqueness and maintain shadow/gshadow.
# Desktop defaults live in the system dconf database; each learner starts with
# a fresh user database rather than a precompiled copy that overrides them.
# Preserve the distribution's shell and application defaults. Remove only
# compiled user overrides and Burp's seed identity before creating box.
for home in /etc/skel /root; do
  rm -f "$home/.config/dconf/user"
  rm -rf "$home/.java/.userPrefs/burp" "$home/.BurpSuite" "$home/.cache"
done
groupadd --gid 1013 box
useradd --uid 1001 --gid 1013 --create-home --shell /bin/bash box
usermod -a -G wireshark box
passwd -l root
passwd -l box
install -d -m 0755 /etc/sudoers.d
printf 'box ALL=(ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/attackbox
chmod 0440 /etc/sudoers.d/attackbox
visudo -cf /etc/sudoers.d/attackbox

# Install AttackBox layout with top launchers and bottom taskbar.
install -D -m 0644 "$PAYLOAD/attackbox.layout" /usr/share/mate-panel/layouts/attackbox.layout
install -D -m 0644 "$PAYLOAD/attackbox.layout" /usr/share/mate-panel/layouts/default.layout

# Ensure Wireshark desktop entry is discoverable at /usr/share/applications/wireshark.desktop.
if [[ ! -f /usr/share/applications/wireshark.desktop ]]; then
  for candidate in /usr/share/applications/org.wireshark.Wireshark.desktop /usr/share/applications/parrot-wireshark.desktop; do
    if [[ -f "$candidate" ]]; then
      cp "$candidate" /usr/share/applications/wireshark.desktop
      break
    fi
  done
fi

# Keep theme settings separate from the project's authoritative panel layout.
rm -f /etc/dconf/db/local.d/parrot-skel /etc/dconf/db/local.d/htb-config
install -d /etc/dconf/db/local.d
python3 "$PAYLOAD/desktop_check.py" theme \
  /usr/lib/parrot-skel/etc/dconf/db/local.d/htb-config /etc/dconf/db/local.d/10-theme

install -d /etc/dconf/profile
printf 'user-db:user\nsystem-db:local\n' > /etc/dconf/profile/user
install -m 0644 "$PAYLOAD/mate-defaults.ini" /etc/dconf/db/local.d/zz-attackbox
dconf update
python3 "$PAYLOAD/desktop_check.py" settings

printf 'en_US.UTF-8 UTF-8\nzh_CN.UTF-8 UTF-8\n' > /etc/locale.gen
locale-gen
update-locale LANG=en_US.UTF-8
# Fail the build if the requested locales were not actually generated.
for language in en_US.UTF-8 zh_CN.UTF-8; do
  env -i PATH=/usr/bin:/bin LANG="$language" LC_ALL="$language" \
    python3 -c 'import locale; locale.setlocale(locale.LC_ALL, "")'
done
printf 'LANG=en_US.UTF-8\n' > /etc/default/locale
printf 'LANG=en_US.UTF-8\n' > /etc/environment

install -D -m 0755 "$PAYLOAD/bin/burpsuite" /usr/local/bin/burpsuite
install -D -m 0644 "$PAYLOAD/applications/burpsuite.desktop" /usr/share/applications/burpsuite.desktop

python3 "$PAYLOAD/desktop_defaults.py" /etc/skel /usr/share/applications
python3 "$PAYLOAD/desktop_defaults.py" /home/box /usr/share/applications
install -D -m 0644 "$PAYLOAD/chromium-policy.json" /etc/chromium/policies/managed/attackbox.json
chown -R 1001:1013 /home/box

printf 'attackbox\n' > /etc/hostname
printf '127.0.0.1 localhost\n127.0.1.1 attackbox trytopwn\n::1 localhost ip6-localhost\n' > /etc/hosts

install -d /usr/share/attackbox
install -m 0644 "$PAYLOAD/burp-user-config.json" /usr/share/attackbox/burp-user-config.json
python3 "$PAYLOAD/desktop_check.py" static /
# The repository owner authorizes accepting Burp Community terms during CI.
runuser -u box -- /usr/bin/env HOME=/home/box LANG=en_US.UTF-8 \
  python3 "$PAYLOAD/burp_ca.py" initialize
install -m 0644 /home/box/.local/share/attackbox/burp-ca.der /usr/share/attackbox/burp-ca.der
# Current Chromium uses the XDG data directory for its NSS certificate database.
install -d -m 0700 -o 1001 -g 1013 /home/box/.local/share/pki /home/box/.local/share/pki/nssdb
runuser -u box -- certutil -N -d sql:/home/box/.local/share/pki/nssdb --empty-password
runuser -u box -- certutil -A -d sql:/home/box/.local/share/pki/nssdb \
  -n AttackBox-Burp -t 'C,,' -i /usr/share/attackbox/burp-ca.der
install -m 0644 "$PAYLOAD/packages.txt" "$PAYLOAD/desktop-packages.txt" "$PAYLOAD/remove-packages.txt" /usr/share/attackbox/
LC_ALL=C getcap -r /usr | LC_ALL=C sort > /usr/share/attackbox/file-capabilities.txt
dpkg-query -W -f='${binary:Package}\t${Version}\t${Installed-Size}\n' > /usr/share/attackbox/packages.tsv
printf '{"format":1,"uid":1001,"gid":1013}\n' > /etc/.attackbox_golden_ready
chmod 0444 /etc/.attackbox_golden_ready
apt-get clean
