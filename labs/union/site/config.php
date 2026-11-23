<?php
// Qualifier site DB credentials deliberately reused by the OS account,
// as described in the 2021 Union walkthrough. Not a production pattern.
session_start();
$servername = "127.0.0.1";
$username = "uhc";
$password = "uhc-11qual-global-pw";
$dbname = "november";
mysqli_report(MYSQLI_REPORT_OFF);
$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_errno) {
    http_response_code(503);
    exit("Service unavailable");
}
