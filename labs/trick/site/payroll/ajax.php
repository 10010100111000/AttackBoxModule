<?php
session_start();
require_once __DIR__ . '/admin_class.php';

if (($_GET['action'] ?? '') !== 'login' || $_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(404);
    exit('3');
}

$username = (string)($_POST['username'] ?? '');
$password = (string)($_POST['password'] ?? '');

$admin = new PayrollAdmin();
if ($admin->login($username, $password)) {
    $_SESSION['payroll_admin'] = true;
    echo '1';
} else {
    echo '3';
}
