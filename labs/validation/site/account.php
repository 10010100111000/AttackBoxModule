<?php
require __DIR__ . '/config.php';
$cookie = (string)($_COOKIE['user'] ?? '');
if (!preg_match('/^[a-f0-9]{32}$/', $cookie)) {
    header('Location: /', true, 302);
    exit;
}
$statement = $conn->prepare(
    'SELECT username, country FROM registration WHERE userhash = ? ORDER BY regtime DESC, id DESC LIMIT 1'
);
$statement->bind_param('s', $cookie);
$statement->execute();
$result = $statement->get_result();
$current = $result ? $result->fetch_assoc() : null;
if (!$current) {
    header('Location: /', true, 302);
    exit;
}
$username = $current['username'];
$country = $current['country'];
// Genuine SECOND-order SQL injection: country was stored using a prepared
// INSERT and is now interpolated UNSAFELY into a different SELECT statement.
$sql = "SELECT username FROM registration WHERE country = '" . $country . "'";
$players = $conn->query($sql);
?>
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="/style.css"></head>
<body><div class="container"><h1 class="page-title">Join the UHC - September Qualifiers</h1></div>
<section class="dark-section"><div class="container inner">
 <h1>Welcome <?php echo htmlspecialchars($username, ENT_QUOTES, 'UTF-8'); ?></h1>
 <h3>Other Players In <?php echo htmlspecialchars($country, ENT_QUOTES, 'UTF-8'); ?></h3>
 <ul>
<?php
if ($players instanceof mysqli_result) {
    while ($player = $players->fetch_assoc()) {
        echo '<li>' . htmlspecialchars((string)$player['username'], ENT_QUOTES, 'UTF-8') . '</li>';
    }
} else {
    echo '<li class="error">Unable to retrieve players.</li>';
}
?>
 </ul></div></section></body></html>
