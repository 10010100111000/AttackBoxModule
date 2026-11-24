<?php
function layout_start($title) {
  $t=htmlspecialchars($title,ENT_QUOTES,'UTF-8');
  echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'.$t.' | Alert</title><link rel="stylesheet" href="/assets/style.css"></head><body><header><div class="wrap nav"><a class="logo" href="/index.php">ALERT<span>.</span></a><nav><a href="/index.php?page=alert">Markdown Viewer</a><a href="/index.php?page=about">About</a><a href="/index.php?page=contact">Contact</a><a href="/index.php?page=donate">Donate</a></nav></div></header><main class="wrap">';
}
function layout_end() { echo '</main><footer>Alert — visualize your Markdown with ease</footer></body></html>'; }
