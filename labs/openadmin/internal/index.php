<?php
session_start();
$error = "";
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $username = isset($_POST["username"]) ? $_POST["username"] : "";
    $password = isset($_POST["password"]) ? $_POST["password"] : "";
    if ($username === "jimmy" && hash("sha512", $password) === "00e302ccdcf1c60b8ad50ea50cf72b939705f49f40f0dc658801b4680b7d758eebdc2e9f9ba8ba3ef8a8bb9a796d34ba2e856838ee9bdde852b8ec3b3a0523b1") {
        $_SESSION["username"] = "jimmy";
        header("Location: main.php");
        exit;
    }
    $error = "Invalid credentials";
}
?>
<!doctype html>
<html><head><meta charset="utf-8"><title>OpenAdmin Trusted</title></head>
<body>
<h2>OpenAdmin Trusted</h2>
<form method="post" action="/index.php">
<label>Username <input name="username" autocomplete="username"></label>
<label>Password <input name="password" type="password" autocomplete="current-password"></label>
<button type="submit">Login</button>
</form>
<p><?= htmlspecialchars($error, ENT_QUOTES, "UTF-8") ?></p>
</body></html>
