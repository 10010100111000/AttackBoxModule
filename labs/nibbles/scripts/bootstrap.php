<?php
// Run the vendor's own one-click installer during Docker build.
chdir('/var/www/localhost/htdocs/nibbleblog');
putenv('HTTP_HOST=127.0.0.1');
putenv('SCRIPT_NAME=/nibbleblog/install.php');
$_SERVER['HTTP_HOST'] = '127.0.0.1';
$_SERVER['SCRIPT_NAME'] = '/nibbleblog/install.php';
$_SERVER['REQUEST_METHOD'] = 'POST';
$_GET = array('language' => 'en_US');
$_POST = array(
    'name' => 'Nibbles',
    'slogan' => 'A small corner of the internet',
    'url' => 'http://127.0.0.1/nibbleblog/',
    'path' => '/nibbleblog/',
    'email' => 'nibbles@nibbles.local',
    'username' => 'admin',
    'password' => 'nibbles'
);
ob_start();
require '/var/www/localhost/htdocs/nibbleblog/install.php';
ob_end_clean();
foreach (array('content/private/config.xml','content/private/users.xml','content/private/shadow.php') as $file) {
    if (!is_file($file) || filesize($file) < 10) {
        fwrite(STDERR, "Vendor installer failed to create " . $file . "\n");
        exit(1);
    }
}
echo "Original Nibbleblog installer initialized XML database\n";
