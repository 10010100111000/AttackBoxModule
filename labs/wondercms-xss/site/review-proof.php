<?php
/**
 * Flag objective only; it does not process untrusted XSS input.
 * Access is controlled by the original CMS's native logged-in session.
 */
declare(strict_types=1);
if (session_status() !== PHP_SESSION_ACTIVE) {
    session_start();
}
header('Cache-Control: no-store, private');
header('X-Content-Type-Options: nosniff');
if (empty($_SESSION['loggedIn']) || ($_SESSION['rootDir'] ?? '') !== __DIR__) {
    http_response_code(403);
    echo 'Forbidden';
    return;
}
header('Content-Type: text/plain; charset=utf-8');
readfile('/run/wcms/review.flag');
