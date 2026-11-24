<?php
require_once __DIR__.'/functions.php';
$pdo = pdo_connect_mysql();
$page = isset($_GET['page']) ? $_GET['page'] : 'home';
shop_header('Collection');
// The real PHP inclusion boundary: file_exists and automatic .php suffix.
if (file_exists($page . '.php')) {
    include $page . '.php';
} else {
    include __DIR__.'/home.php';
}
shop_footer();
