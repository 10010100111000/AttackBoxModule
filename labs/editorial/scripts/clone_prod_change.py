#!/usr/local/bin/python3
"""Original-style deployment helper, deliberately uses vulnerable GitPython."""
import os
import sys
from git import Repo

if len(sys.argv) != 2:
    print("Usage: clone_prod_change.py <repository-url>", file=sys.stderr)
    raise SystemExit(2)
# The URL is intentionally untrusted, and GitPython 3.1.29 passes it
# to the REAL git binary with the ext protocol enabled (CVE-2022-24439).
# Do not replace this with a mock shell endpoint.
target = "/tmp/prod-review-" + str(os.getpid())
Repo.clone_from(sys.argv[1], target, multi_options=["-c protocol.ext.allow=always"])
