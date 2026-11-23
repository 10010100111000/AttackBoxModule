<?php
/**
 * Seed the authentic upstream WonderCMS file database and private per-instance
 * challenge material. The vulnerable upstream index.php is not modified.
 */
declare(strict_types=1);
$admin = getenv('WONDERCMS_ADMIN_PASSWORD') ?: '';
$flag = getenv('WONDERCMS_STATIC_XSS_FLAG') ?: '';
$strict = getenv('WONDERCMS_REQUIRE_PRIVATE_FLAGS') === '1';
if ($strict && ($admin === '' || $flag === '')) {
    fwrite(STDERR, "WonderCMS: admin password and instance XSS flag are required\n");
    exit(1);
}
if ($admin === '') $admin = bin2hex(random_bytes(16));
if ($flag === '') $flag = 'TTP{wondercms_demo_xss_only}';
if (strlen($admin) < 12 || strlen($flag) > 256) {
    fwrite(STDERR, "WonderCMS: invalid instance values\n");
    exit(1);
}

$path = '/srv/wcms/data/database.js';
if (!file_exists($path)) {
    define('PHPUNIT_TESTING', true);
    $_SERVER['SERVER_PORT'] = '80';
    $_SERVER['SERVER_NAME'] = 'localhost';
    $_SERVER['HTTP_HOST'] = 'localhost';
    $_SERVER['SCRIPT_NAME'] = '/index.php';
    require '/srv/wcms/index.php';
    new Wcms();
}
$db = json_decode(file_get_contents($path));
if (!is_object($db) || !isset($db->config, $db->pages)) {
    fwrite(STDERR, "WonderCMS: upstream initialisation failed\n");
    exit(1);
}
$db->config->password = password_hash($admin, PASSWORD_DEFAULT);
$db->config->siteTitle = 'Northbound Press';
$db->config->lastModulesSync = time();
$db->pages->home->title = 'Northbound Press';
$db->pages->home->content = '<h1>Stories worth discovering.</h1><p>Independent publishing and thoughtful editorial work.</p><p>Read about our submissions and how we work with new writers.</p><p><a href="/contact.php">Contact the editorial team</a></p>';
$db->pages->{'how-to'}->title = 'Submissions';
$db->pages->{'how-to'}->content = '<h2>Work with us</h2><p>Northbound Press accepts proposals and articles from new writers. Please contact the editorial office to arrange a review.</p><p><a href="/contact.php">Send us your website</a></p>';
if (file_put_contents($path, json_encode($db, JSON_FORCE_OBJECT | JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE), LOCK_EX) === false) {
    fwrite(STDERR, "WonderCMS: cannot write native database\n");
    exit(1);
}
chmod($path, 0600);
@chown($path, 'www-data');
@chgrp($path, 'www-data');

$flagPath = '/run/wcms/review.flag';
file_put_contents($flagPath, $flag . "\n", LOCK_EX);
chmod($flagPath, 0600);
chown($flagPath, 'www-data');
chgrp($flagPath, 'www-data');

$botConfig = '/run/wcms/bot-config.json';
file_put_contents($botConfig, json_encode(['admin_password' => $admin], JSON_THROW_ON_ERROR), LOCK_EX);
chmod($botConfig, 0600);
chown($botConfig, 'wcmsbot');
chgrp($botConfig, 'wcmsbot');

@mkdir('/run/wcms/reports', 0770, true);
chown('/run/wcms/reports', 'www-data');
chgrp('/run/wcms/reports', 'wcmsbot');
chmod('/run/wcms/reports', 02770);

fwrite(STDOUT, "WonderCMS 3.4.2 and private admin-review configuration initialised\n");
