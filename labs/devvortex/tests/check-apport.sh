#!/bin/bash
set -euo pipefail
EXPECTED='2.20.11-0ubuntu82'
for pkg in apport python3-apport python3-problem-report; do
    actual=$(dpkg-query -W -f='${Version}' "$pkg")
    [[ "$actual" == "$EXPECTED" ]] || { echo "FAIL: $pkg version $actual (want $EXPECTED)" >&2; exit 1; }
done
[[ -f /usr/bin/apport-cli ]] || { echo 'FAIL: upstream apport-cli missing' >&2; exit 1; }
[[ $(readlink -f /usr/bin/apport-cli) == /usr/bin/apport-cli ]] || { echo 'FAIL: apport-cli replaced by a symlink' >&2; exit 1; }
/usr/bin/apport-cli --version | grep -Fq '2.20.11' || { echo 'FAIL: apport-cli version mismatch' >&2; exit 1; }
sudo -l -U logan | grep -Fq /usr/bin/apport-cli || { echo 'FAIL: sudo authorization missing' >&2; exit 1; }
printf 'PASS: genuine pre-fix Ubuntu Apport packages and sudo policy installed\n'
printf 'NOTE: interactive pager escape still needs an isolated runtime check\n'
