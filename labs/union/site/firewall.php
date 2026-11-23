<?php
require('config.php');
if (empty($_SESSION['Authenticated'])) {
    echo 'Access Denied';
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
<?php
// Intentionally recreates the ORIGINAL unsafe shell call, not a mock.
// Requires Docker NET_ADMIN in the isolated instance network namespace.
if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
    $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
} else {
    $ip = $_SERVER['REMOTE_ADDR'];
}
error_log("Union CI diagnostic: forwarded=" . (isset($_SERVER["HTTP_X_FORWARDED_FOR"]) ? "yes" : "no"));
$diagnostic_output = system("exec 2>&1; sudo /usr/sbin/iptables -A INPUT -s " . $ip . " -j ACCEPT", $command_status);
error_log("Union CI diagnostic: last_output=" . (string)$diagnostic_output);
error_log("Union CI diagnostic: shell_exit=" . $command_status);
?>
    <h1 class="text-white">Welcome Back!</h1>
    <h3 class="text-white">Your IP Address has now been granted SSH Access.</h3>
  </div>
</section>
</body>
</html>
