<?php
// The beta tracker parses XML with PHP's real libxml implementation.
// Deliberate XXE configuration reproduces the retired training machine.
header('Content-Type: text/html; charset=UTF-8');
if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_POST['data'])) {
    http_response_code(400);
    exit('No report supplied.');
}
$encoded = (string)$_POST['data'];
$payload = base64_decode($encoded, true);
if ($payload === false || strlen($payload) > 16384) {
    http_response_code(400);
    exit('Invalid report data.');
}
libxml_use_internal_errors(true);
$report = simplexml_load_string($payload, 'SimpleXMLElement', LIBXML_NOENT);
if ($report === false || $report->getName() !== 'bugreport') {
    http_response_code(400);
    exit('Could not parse report XML.');
}
$title = (string)$report->title;
$cwe = (string)$report->cwe;
$cvss = (string)$report->cvss;
$reward = (string)$report->reward;
echo '<div class="report-receipt">';
echo '<strong>If DB were ready, would have added:</strong><p>';
echo 'Title: ' . nl2br(htmlspecialchars($title, ENT_QUOTES, 'UTF-8')) . '<br>';
echo 'CWE: ' . nl2br(htmlspecialchars($cwe, ENT_QUOTES, 'UTF-8')) . '<br>';
echo 'CVSS: ' . nl2br(htmlspecialchars($cvss, ENT_QUOTES, 'UTF-8')) . '<br>';
echo 'Reward: ' . nl2br(htmlspecialchars($reward, ENT_QUOTES, 'UTF-8')) . '</p></div>';
