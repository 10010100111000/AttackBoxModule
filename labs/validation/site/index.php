<?php
// UHC September 2021 registration flow — independently reconstructed.
require __DIR__ . '/config.php';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = (string)($_POST['username'] ?? '');
    $country = (string)($_POST['country'] ?? '');
    if (strlen($username) < 1 || strlen($username) > 90 ||
        strlen($country) < 1 || strlen($country) > 1024) {
        http_response_code(400);
        exit('Invalid registration.');
    }
    $userhash = md5($username);
    // INSERT is intentionally parameterized, matching the original's
    // SECOND-order flaw: exploit happens later when reading the stored row.
    $statement = $conn->prepare(
        'INSERT INTO registration (username, userhash, country, regtime) VALUES (?, ?, ?, ?)'
    );
    if (!$statement) {
        http_response_code(503);
        exit('Service temporarily unavailable.');
    }
    $now = time();
    $statement->bind_param('sssi', $username, $userhash, $country, $now);
    if (!$statement->execute()) {
        http_response_code(503);
        exit('Unable to register at this time.');
    }
    setcookie('user', $userhash, ['path'=>'/', 'httponly'=>true, 'samesite'=>'Lax']);
    header('Location: /account.php', true, 302);
    exit;
}
?>
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="/style.css"></head>
<body>
<div class="container"><h1 class="page-title">Join the UHC - September Qualifiers</h1></div>
<section class="dark-section">
 <div class="container inner">
  <h1>Join the UHC Qualifiers</h1>
  <p>Register for the September qualifiers.</p>
  <form action="/" method="post">
   <label class="sr-only" for="username">Username</label>
   <input type="text" id="username" name="username" placeholder="Username" maxlength="90" required>
   <label class="sr-only" for="country">Country</label>
   <select id="country" name="country" required>
    <option value="Belgium">Belgium</option>
    <option value="Brazil">Brazil</option>
    <option value="Canada">Canada</option>
    <option value="Germany">Germany</option>
    <option value="India">India</option>
    <option value="Indonesia">Indonesia</option>
    <option value="United Kingdom">United Kingdom</option>
    <option value="United States">United States</option>
   </select>
   <button type="submit">Join Now</button>
  </form>
 </div>
</section>
</body></html>
