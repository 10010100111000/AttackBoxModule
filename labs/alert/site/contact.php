<?php
if($_SERVER['REQUEST_METHOD']!=='POST') { http_response_code(405); exit('Invalid request.'); }
$email=filter_var($_POST['email']??'',FILTER_SANITIZE_EMAIL);
$msg=htmlspecialchars((string)($_POST['message']??''),ENT_QUOTES,'UTF-8');
if(!$email||!$msg||strlen($msg)>4096) { http_response_code(400); exit('Email and message required.'); }
$name=gmdate('Y-m-d_H-i-s').'-'.bin2hex(random_bytes(4)).'.txt';
file_put_contents(__DIR__.'/messages/'.$name,"Email: ".$email."\n\nMessage: ".$msg);
// Admin checks links in contact messages. The bot is part of this target
// container, not the platform Worker. It reads the file as an admin would.
$queue=['message'=>$name,'id'=>bin2hex(random_bytes(6))];
file_put_contents('/run/alert/queue/'.bin2hex(random_bytes(12)).'.json',json_encode($queue));
header('Location: /index.php?page=contact&status=sent',true,303);
