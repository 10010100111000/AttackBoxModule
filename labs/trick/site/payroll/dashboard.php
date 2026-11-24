<?php
session_start();
if (empty($_SESSION['payroll_admin'])) {
    header('Location: /');
    exit;
}
?>
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Payroll Overview</title><link rel="stylesheet" href="/assets/payroll.css"></head>
<body>
  <main class="dashboard">
    <header><strong>Payroll Management System</strong><a href="/">Sign out</a></header>
    <section class="panel wide">
      <p class="kicker">ADMINISTRATION</p>
      <h1>Payroll overview</h1>
      <p class="muted">The current payroll period is ready for review.</p>
      <div class="stats"><article><span>Employees</span><strong>24</strong></article><article><span>Pending reviews</span><strong>03</strong></article><article><span>Current period</span><strong>November</strong></article></div>
    </section>
  </main>
</body>
</html>
