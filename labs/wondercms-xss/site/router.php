<?php
/**
 * Path router for the authentic WonderCMS entrypoint.
 * It substitutes only for Apache rewrite and access-control rules.
 */
declare(strict_types=1);

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?: '/';

if ($path === '/healthz') {
    header('Content-Type: application/json');
    echo json_encode(['status' => 'ok', 'component' => 'wondercms']);
    return true;
}

if ($path === '/bot-healthz') {
    $ready = '/run/wcms/bot.ready';
    if (!is_file($ready) || (time() - filemtime($ready)) > 120) {
        http_response_code(503);
        header('Content-Type: application/json');
        echo json_encode(['status' => 'unavailable', 'component' => 'admin-review-bot']);
        return true;
    }
    header('Content-Type: application/json');
    echo json_encode(['status' => 'ok', 'component' => 'admin-review-bot']);
    return true;
}

if ($path === '/review-proof.php') {
    require __DIR__ . '/review-proof.php';
    return true;
}

// Apache's upstream .htaccess denies direct data/backup/config access.
// PHP's development server does not read .htaccess, so mirror that rule.
if (preg_match('~^/(?:data|\.git)(?:/|$)~i', $path)
    || in_array($path, ['/LICENSE-WonderCMS', '/version', '/.htaccess', '/router.php'], true)) {
    http_response_code(404);
    echo 'Not found';
    return true;
}

if ($path !== '/' && is_file(__DIR__ . $path)) {
    return false;
}

if (!isset($_GET['page'])) {
    $_GET['page'] = trim($path, '/');
}
require __DIR__ . '/index.php';
return true;
