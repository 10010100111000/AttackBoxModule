<?php
require('config.php');
$_SESSION['Authenticated'] = false;
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $sql = "SELECT one FROM flag WHERE one = ?";
    $stmt = $conn->prepare($sql);
    if ($stmt) {
        $flag = (string)($_POST['flag'] ?? '');
        $stmt->bind_param('s', $flag);
        $stmt->execute();
        $stmt->store_result();
        if ($stmt->num_rows === 1) {
            $_SESSION['Authenticated'] = true;
            header('Location: /firewall.php', true, 302);
            exit;
        }
    }
}
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container">
  <h1 class="text-center m-5">Join the UHC - November Qualifiers</h1>
</div>
<section class="bg-dark text-center p-5 mt-4">
  <div class="container p-5">
    <h1 class="text-white">Qualifier Challenge</h1>
    <form action="/challenge.php" method="post" class="form-inline justify-content-center mt-4">
      <label for="flag" class="sr-only">Flag</label>
      <input type="text" class="form-control mr-2" id="flag" name="flag" placeholder="Enter flag" required>
      <button class="btn btn-primary" type="submit">Submit</button>
    </form>
  </div>
</section>
</body>
</html>
