<?php
session_start();
if (!isset($_SESSION["username"])) {
    header("Location: /index.php");
    exit;
}
$output = shell_exec("cat /home/joanna/.ssh/id_rsa");
?>
<!doctype html>
<html><head><meta charset="utf-8"><title>OpenAdmin Trusted</title></head>
<body>
<h2>OpenAdmin Trusted</h2>
<pre><?= htmlspecialchars($output, ENT_QUOTES, "UTF-8") ?></pre>
<h3>Don't forget your "ninja" password</h3>
<a href="/logout.php">Logout</a>
</body></html>
