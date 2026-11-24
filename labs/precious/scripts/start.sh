#!/bin/sh
set -eu
if [ -n "${PRECIOUS_USER_FLAG:-}" ]; then
  printf '%s\n' "$PRECIOUS_USER_FLAG" > /home/ruby/user.txt
  chown ruby:ruby /home/ruby/user.txt
  chmod 0400 /home/ruby/user.txt
fi
unset PRECIOUS_USER_FLAG
cd /app
exec su -s /bin/sh ruby -c 'exec ruby /app/app.rb'
