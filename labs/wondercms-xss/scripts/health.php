<?php
$url = 'http://127.0.0.1:8080/healthz';
$context = stream_context_create(['http' => ['timeout' => 2]]);
$result = @file_get_contents($url, false, $context);
exit($result !== false && strpos($result, '"status":"ok"') !== false ? 0 : 1);
