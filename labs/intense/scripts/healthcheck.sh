#!/bin/sh
set -eu
curl -fsS --max-time 3 http://127.0.0.1:8080/healthz >/dev/null
