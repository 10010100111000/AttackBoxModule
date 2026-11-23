<?php
foreach (['healthz', 'bot-healthz'] as $path) {
    $url = 'http://127.0.0.1:8080/' . $path;
    $context = stream_context_create(['http' => ['timeout' => 3]]);
    $result = @file_get_contents($url, false, $context);
    if ($result === false || strpos($result, '"status":"ok"') === false) {
        exit(1);
    }
}
exit(0);
