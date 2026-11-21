#!/usr/bin/env bash
# Package policy shared by image construction and acceptance checks.
read_packages() {
  local file=$1 line
  local -n result=$2
  result=()
  [[ -r $file ]] || { echo "Missing package list: $file" >&2; return 1; }
  while IFS= read -r line || [[ -n $line ]]; do
    line=${line%%#*}
    line=${line#"${line%%[![:space:]]*}"}
    line=${line%"${line##*[![:space:]]}"}
    [[ -n $line ]] || continue
    [[ $line =~ ^[a-z0-9][a-z0-9+.-]+$ ]] || { echo "Invalid package in $file: $line" >&2; return 1; }
    result+=("$line")
  done < "$file"
}

remove_packages() {
  local file=$1 package action _remainder plan
  local -a requested installed
  local -A allowed=()
  read_packages "$file" requested || return
  installed=()
  for package in "${requested[@]}"; do
    allowed[$package]=1
    if [[ $(dpkg-query -W -f='${db:Status-Status}' "$package" 2>/dev/null) == installed ]]; then
      installed+=("$package")
    fi
  done
  ((${#installed[@]})) || return 0
  if ! plan=$(apt-get -s -o APT::Get::AutomaticRemove=false purge "${installed[@]}"); then
    printf '%s\n' "$plan" >&2
    return 1
  fi
  printf '%s\n' "$plan"
  while read -r action package _remainder; do
    if [[ $action == Remv || $action == Purg ]]; then
      package=${package%%:*}
      [[ ${allowed[$package]:-} == 1 ]] || {
        echo "Removal would also delete $package; review $file before continuing" >&2
        return 1
      }
    fi
  done <<< "$plan"
  apt-get purge -y -o APT::Get::AutomaticRemove=false "${installed[@]}"
}
