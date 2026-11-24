<?php
// Original design relies on loopback trust; public callers see no content.
if(!in_array($_SERVER['REMOTE_ADDR']??'',['127.0.0.1','::1'],true)) { http_response_code(403); exit('Forbidden'); }
$dir=__DIR__.'/messages/';
if(isset($_GET['file'])) {
 $file=(string)$_GET['file'];
 // Intentionally vulnerable real filesystem read; not a fake flag endpoint.
 $contents=@file_get_contents($dir.$file);
 if($contents===false) { http_response_code(404); exit('Not found'); }
 echo '<pre>'.htmlspecialchars($contents,ENT_QUOTES,'UTF-8').'</pre>';
} else {
 echo '<h1>Messages</h1><ul>';
 foreach(glob($dir.'*.txt') as $f) { $name=basename($f); echo '<li><a href="/messages.php?file='.rawurlencode($name).'">'.htmlspecialchars($name).'</a></li>'; }
 echo '</ul>';
}
