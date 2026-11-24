<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Payroll Management System</title>
  <link rel="stylesheet" href="/assets/payroll.css">
</head>
<body>
  <main class="shell">
    <section class="brand">
      <div class="mark">P</div>
      <div><strong>Payroll</strong><span>Management System</span></div>
    </section>
    <section class="panel">
      <p class="kicker">EMPLOYEE SERVICES</p>
      <h1>Sign in to your account</h1>
      <p class="muted">Use your employee credentials to continue.</p>
      <form id="login">
        <label for="username">Username</label>
        <input id="username" name="username" autocomplete="username" required>
        <label for="password">Password</label>
        <input id="password" name="password" type="password" autocomplete="current-password" required>
        <button type="submit">Sign in</button>
        <p id="message" role="status" aria-live="polite"></p>
      </form>
      <footer>Payroll services · Internal access</footer>
    </section>
  </main>
  <script>
    document.querySelector('#login').addEventListener('submit', async (event) => {
      event.preventDefault();
      const form = new FormData(event.currentTarget);
      const body = new URLSearchParams(form);
      const response = await fetch('/ajax.php?action=login', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body
      });
      const result = (await response.text()).trim();
      if (result === '1') {
        location.href = '/dashboard.php';
      } else {
        document.querySelector('#message').textContent = 'The username or password is incorrect.';
      }
    });
  </script>
</body>
</html>
