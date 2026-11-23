<?php
require('config.php');
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    header('Content-Type: text/html; charset=UTF-8');
    $player = (string)($_POST['player'] ?? '');
    // Deliberately weak keyword filtering matching the original writeup's
    // WAF annoyance. This is NOT a SQL injection mitigation.
    if (stripos($player, ' or ') !== false || stripos($player, '0x') !== false) {
        echo 'Congratulations ' . htmlspecialchars($player, ENT_QUOTES, 'UTF-8') . ' you may compete in this tournament!';
        exit;
    }
    // Genuine SQLi: the supplied value is interpolated in a real MariaDB
    // SELECT. SQL engine evaluates UNION/LOAD_FILE/INFORMATION_SCHEMA.
    $query = "SELECT player FROM players WHERE player = '" . $player . "'";
    $result = $conn->query($query);
    if ($result && $result->num_rows > 0) {
        $row = $result->fetch_row();
        echo "Sorry, " . $row[0] . " you are not eligible due to already qualifying.";
    } elseif ($result) {
        echo "Congratulations " . htmlspecialchars($player, ENT_QUOTES, 'UTF-8') .
             ' you may compete in this tournament!<br /><br />Complete the challenge <a href="/challenge.php">here</a>';
    } else {
        echo 'Congratulations ' . htmlspecialchars($player, ENT_QUOTES, 'UTF-8') . ' you may compete in this tournament!';
    }
    exit;
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
    <h1 class="text-white">Player Eligibility Check</h1>
    <form id="eligibility-form" class="form-inline justify-content-center mt-4">
      <label for="player" class="sr-only">Player</label>
      <input id="player" name="player" type="text" class="form-control mr-2" placeholder="Enter player name" autocomplete="off" required>
      <button type="submit" class="btn btn-primary">Check</button>
    </form>
    <div id="result" class="text-white mt-4" aria-live="polite"></div>
  </div>
</section>
<script src="/site.js"></script>
</body>
</html>
