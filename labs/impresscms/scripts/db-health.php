<?php
require '/var/www/html/mainfile.php';
$dsn = 'mysql:host=' . XOOPS_DB_HOST . ';dbname=' . XOOPS_DB_NAME . ';charset=utf8';
$pdo = new PDO($dsn, XOOPS_DB_USER, XOOPS_DB_PASS, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_TIMEOUT => 3,
]);
$pdo->query('SELECT 1')->fetchColumn();
