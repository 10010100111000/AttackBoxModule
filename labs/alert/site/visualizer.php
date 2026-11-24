<?php
require __DIR__.'/common.php';
$uploads=__DIR__.'/uploads';
$filename=null;
if(isset($_GET['link_share'])) {
 $name=$_GET['link_share'];
 if(!is_string($name)||!preg_match('/^[a-zA-Z0-9_.-]+\.md$/D',$name)) { http_response_code(400); exit('Invalid file name.'); }
 if(!is_file($uploads.'/'.$name)) { http_response_code(404); exit('Invalid file.'); }
 $filename=$name;
} elseif(isset($_FILES['file']) && is_uploaded_file($_FILES['file']['tmp_name'])) {
 $name=$_FILES['file']['name'];
 if(!is_string($name)||strtolower(pathinfo($name,PATHINFO_EXTENSION))!=='md') { http_response_code(400); exit('Only Markdown documents are supported.'); }
 if($_FILES['file']['size']>65536) { http_response_code(413); exit('Markdown file too large.'); }
 $filename=bin2hex(random_bytes(12)).'.md';
 if(!move_uploaded_file($_FILES['file']['tmp_name'],$uploads.'/'.$filename)) { http_response_code(500); exit('Upload failed.'); }
} else { header('Location: /index.php'); exit; }
$source=file_get_contents($uploads.'/'.$filename);
$cmd='python3 /opt/alert/scripts/render_md.py';
$p=proc_open($cmd,[0=>['pipe','r'],1=>['pipe','w'],2=>['pipe','w']],$pipes);
if(!is_resource($p)) { http_response_code(500); exit('Renderer unavailable.'); }
fwrite($pipes[0],$source); fclose($pipes[0]);
$rendered=stream_get_contents($pipes[1]); fclose($pipes[1]);
$err=stream_get_contents($pipes[2]);fclose($pipes[2]);
if(proc_close($p)!==0) { http_response_code(500); exit('Markdown rendering failed.'); }
layout_start('Markdown Preview');
echo '<section class="preview"><h1>Markdown Preview</h1><div class="rendered">'.$rendered.'</div><p><a class="button" href="/visualizer.php?link_share='.rawurlencode($filename).'">Share Markdown</a></p><p class="url">Share link: <a href="/visualizer.php?link_share='.rawurlencode($filename).'">/visualizer.php?link_share='.htmlspecialchars($filename).'</a></p></section>';
layout_end();
