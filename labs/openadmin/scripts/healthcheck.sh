#!/bin/bash
set -euo pipefail
mysqladmin ping --silent >/dev/null
curl -fsS --max-time 5 http://127.0.0.1/ona/ | grep -F 'v18.1.1' >/dev/null
curl -fsS --max-time 5 http://127.0.0.1:52846/index.php | grep -F 'OpenAdmin Trusted' >/dev/null
php -r '$s=@fsockopen("127.0.0.1",22,$e,$m,3); if (!$s) exit(1); $b=fgets($s); fclose($s); if (strpos($b,"SSH-2.0-")!==0) exit(1);'
