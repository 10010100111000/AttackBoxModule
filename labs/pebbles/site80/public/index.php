<?php
// Pebbles initial PHP page (behavioral reconstruction, not an OffSec source file).
declare(strict_types=1);
session_start();
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');

$error = false;
$loggedIn = isset($_SESSION['pebbles_user']) && is_string($_SESSION['pebbles_user']);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['logout'])) {
        $_SESSION = [];
        session_regenerate_id(true);
        header('Location: /');
        exit;
    }
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';
    if (is_string($username) && is_string($password)
        && strlen($username) <= 128 && strlen($password) <= 128
        && hash_equals((string)getenv('PEBBLES_LOGIN_USER'), $username)
        && ($hash = getenv('PEBBLES_LOGIN_HASH')) !== false && $hash !== ''
        && password_verify($password, $hash)) {
        session_regenerate_id(true);
        $_SESSION['pebbles_user'] = $username;
        header('Location: /');
        exit;
    }
    $error = true;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pebbles</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <main class="login-container">
    <h1>Pebbles</h1>
    <?php if ($loggedIn): ?>
      <p>Signed in.</p>
      <form method="post" action="/"><button type="submit" name="logout" value="1">Log out</button></form>
    <?php else: ?>
      <?php if ($error): ?><p class="error" role="alert">Invalid username or password.</p><?php endif; ?>
      <form method="post" action="/" autocomplete="on">
        <label for="username">Username</label>
        <input id="username" name="username" type="text" autocomplete="username" required>
        <label for="password">Password</label>
        <input id="password" name="password" type="password" autocomplete="current-password" required>
        <button type="submit">Login</button>
      </form>
    <?php endif; ?>
  </main>
</body>
</html>
