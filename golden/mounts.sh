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

# Shared by package installation and disposable desktop acceptance.
mount_rootfs() {
  local target=$1 entry name major minor destination
  install -d "$target/proc" "$target/sys" "$target/dev" "$target/run"
  mount_image -t proc proc "$target/proc"
  mount_image -t sysfs -o ro,nosuid,nodev,noexec sysfs "$target/sys"
  mount_image -t tmpfs -o nosuid,mode=755 tmpfs "$target/dev"
  for entry in 'null 1 3' 'zero 1 5' 'full 1 7' 'random 1 8' 'urandom 1 9' 'tty 5 0'; do
    read -r name major minor <<< "$entry"
    mknod -m 0666 "$target/dev/$name" c "$major" "$minor"
  done
  for entry in 'fd /proc/self/fd' 'stdin /proc/self/fd/0' 'stdout /proc/self/fd/1' 'stderr /proc/self/fd/2'; do
    read -r name destination <<< "$entry"
    ln -s "$destination" "$target/dev/$name"
  done
  mkdir "$target/dev/pts" "$target/dev/shm"
  mount_image -t devpts -o newinstance,ptmxmode=0666,mode=620 devpts "$target/dev/pts"
  ln -s pts/ptmx "$target/dev/ptmx"
  mount_image -t tmpfs -o nosuid,nodev,mode=1777 tmpfs "$target/dev/shm"
  mount_image -t tmpfs -o nosuid,nodev,mode=755 tmpfs "$target/run"
}
