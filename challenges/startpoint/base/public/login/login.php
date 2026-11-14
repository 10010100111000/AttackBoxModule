<?php
session_start();

if (!empty($_POST['username']) && !empty($_POST['password'])) {
    require('config.php');

    if (strcmp($username, $_POST['username']) == 0) {
        if (strcmp($password, $_POST['password']) == 0) {
            $_SESSION['user_id'] = 1;
            header("Location: /upload.php");
            exit;
        } else {
            print("<script>alert('Wrong Username or Password')</script>");
        }
    } else {
        print("<script>alert('Wrong Username or Password')</script>");
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Login - BASE</title>
  <link rel="icon" href="/assets/img/favicon.png">
  <link rel="stylesheet" href="/assets/vendor/bootstrap/css/bootstrap.min.css">
  <link rel="stylesheet" href="/assets/vendor/bootstrap-icons/bootstrap-icons.css">
  <link rel="stylesheet" href="/assets/vendor/aos/aos.css">
  <link rel="stylesheet" href="/assets/css/main.css">
  <link rel="stylesheet" href="/assets/css/base-pages.css">
</head>
<body class="base-login-page">
  <header id="header" class="header d-flex align-items-center sticky-top">
    <div class="container-fluid container-xl position-relative d-flex align-items-center">
      <a href="/" class="logo d-flex align-items-center me-auto"><h1 class="sitename">BASE</h1></a>
      <nav id="navmenu" class="navmenu">
        <ul>
          <li><a href="/#hero">Home</a></li>
          <li><a href="/#about">About</a></li>
          <li><a href="/#services">Services</a></li>
          <li><a href="/#team">Team</a></li>
          <li><a href="/#pricing">Pricing</a></li>
          <li><a href="/#contact">Contact</a></li>
          <li><a class="active" href="/login/login.php">Login</a></li>
        </ul>
        <i class="mobile-nav-toggle d-xl-none bi bi-list"></i>
      </nav>
    </div>
  </header>

  <main class="base-login-main">
    <section class="base-login-panel">
      <div class="container">
        <h1>LOGIN</h1>
        <p>Use the form below to log into your account.</p>
        <form class="base-login-form" method="POST" action="">
          <div class="mb-3">
            <input class="form-control" type="text" name="username" placeholder="Your Username" required>
          </div>
          <div class="mb-3">
            <input class="form-control" type="password" name="password" placeholder="Your Password" required>
          </div>
          <button class="btn btn-primary" type="submit">Log In</button>
        </form>
      </div>
    </section>
  </main>

  <a href="#" id="scroll-top" class="scroll-top d-flex align-items-center justify-content-center"><i class="bi bi-arrow-up-short"></i></a>
  <script src="/assets/vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
  <script src="/assets/vendor/aos/aos.js"></script>
  <script src="/assets/js/main.js"></script>
</body>
</html>
