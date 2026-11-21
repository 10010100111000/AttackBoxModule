#!/usr/bin/env bash
# Executed inside the build rootfs before account and desktop configuration.
set -euo pipefail
PAYLOAD=/tmp/attackbox-build
source "$PAYLOAD/packages.sh"
declare -a packages=() desktop_packages=() removed_packages=()
read_packages "$PAYLOAD/packages.txt" packages
read_packages "$PAYLOAD/desktop-packages.txt" desktop_packages
read_packages "$PAYLOAD/remove-packages.txt" removed_packages
for package in "${packages[@]}" "${desktop_packages[@]}"; do
  for removed in "${removed_packages[@]}"; do
    [[ $package != "$removed" ]] || { echo "Package is both required and removed: $package" >&2; exit 1; }
  done
done
printf 'wireshark-common wireshark-common/install-setuid boolean true\n' | debconf-set-selections
apt-get update -o Acquire::Retries=3 -o APT::Update::Error-Mode=any
apt-get install -y --no-install-recommends -o Acquire::Retries=3 "${packages[@]}"
# The desktop meta-package owns the complete desktop dependency set.
apt-get install -y --install-recommends -o Acquire::Retries=3 "${desktop_packages[@]}"
test -s /etc/apt/sources.list.d/parrot.sources
rm /etc/apt/sources.list
apt-get full-upgrade -y --no-install-recommends -o Acquire::Retries=3
: > "$PAYLOAD/removed-packages.tsv"
for package in "${removed_packages[@]}"; do
  details=$(dpkg-query -W -f='${db:Status-Status}\t${Installed-Size}' "$package" 2>/dev/null || true)
  IFS=$'\t' read -r status size <<< "$details"
  if [[ $status == installed ]]; then
    printf '%s\t%s\n' "$package" "$size" >> "$PAYLOAD/removed-packages.tsv"
  fi
done
remove_packages "$PAYLOAD/remove-packages.txt"
apt-get check
audit="$(dpkg --audit)"
[[ -z "$audit" ]] || { printf '%s\n' "$audit" >&2; exit 1; }
