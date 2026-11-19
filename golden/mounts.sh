#!/usr/bin/env bash
# Track each successful mount, including when a later mount fails.
MOUNTS=()
mount_image() {
  local destination="${!#}"
  mount "$@" || return
  MOUNTS+=("$destination")
}
unmount_image() {
  local index failed=0
  for ((index=${#MOUNTS[@]}-1; index>=0; index--)); do
    if mountpoint -q "${MOUNTS[index]}"; then
      umount "${MOUNTS[index]}" || failed=1
    fi
  done
  ((failed == 0)) || return 1
  MOUNTS=()
}
