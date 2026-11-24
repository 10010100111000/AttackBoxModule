<?php
require __DIR__.'/common.php';
$page=$_GET['page'] ?? 'alert';
if(!in_array($page,['alert','contact','about','donate'],true)) $page='alert';
layout_start('Markdown Visualizer');
if($page==='alert') {
 echo '<section class="hero"><p class="eyebrow">MARKDOWN TOOL</p><h1>Visualize your Markdown</h1><p>Upload a Markdown file to preview your notes, drafts and documents, or share your document with a collaborator.</p></section><section class="panel"><h2>Upload your Markdown file</h2><form method="post" action="/visualizer.php" enctype="multipart/form-data"><label for="md">Choose a .md file</label><input type="file" name="file" id="md" accept=".md" required><button>View Markdown</button></form></section>';
} elseif ($page==='contact') {
 echo '<section class="hero small"><h1>Contact Us</h1><p>Send a message to our team. Our administrator reviews messages regularly.</p></section><section class="panel"><form action="/contact.php" method="post"><label>Email</label><input type="email" name="email" required><label>Message</label><textarea name="message" rows="6" required></textarea><button>Send Message</button></form></section>';
} elseif ($page==='about') {
 echo '<section class="hero small"><h1>About Alert</h1><p>A simple Markdown visualizer designed for sharing documents.</p></section>';
} else {
 echo '<section class="hero small"><h1>Support Us</h1><p>Help support independent writing tools.</p></section><section class="panel"><label>Amount</label><input type="number" min="1"><button>Donate</button></section>';
}
layout_end();
