#!/bin/sh
set -eu

# Per-instance target flags; the Worker forwards values but never judges them.
if [ -n "$NODEBLOG_USER_FLAG" ]; then
  printf '%s\n' "$NODEBLOG_USER_FLAG" > /home/nodeblog/user.txt
  chmod 0600 /home/nodeblog/user.txt
fi
unset NODEBLOG_USER_FLAG

mkdir -p /data/mongo
mongod --bind_ip 127.0.0.1 --port 27017 --dbpath /data/mongo \
  --wiredTigerCacheSizeGB 0.25 --quiet --logpath /data/mongod.log &
mongo_pid=$!
web_pid=''

stop_children() {
  if [ -n "$web_pid" ]; then kill "$web_pid" 2>/dev/null || true; fi
  kill "$mongo_pid" 2>/dev/null || true
  wait "$mongo_pid" 2>/dev/null || true
  if [ -n "$web_pid" ]; then wait "$web_pid" 2>/dev/null || true; fi
}
trap stop_children TERM INT EXIT

n=0
until node /opt/blog/seed.js; do
  n=$((n + 1))
  if [ "$n" -ge 50 ] || ! kill -0 "$mongo_pid" 2>/dev/null; then
    echo "MongoDB failed to initialize" >&2
    exit 1
  fi
  sleep 2
done

node /opt/blog/server.js &
web_pid=$!
wait "$web_pid"
