<?php
$message = '';
$link = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['zip_file'])) {
    $uploaded = $_FILES['zip_file'];
    $ext = strtolower(pathinfo($uploaded['name'], PATHINFO_EXTENSION));
    if ($uploaded['error'] !== UPLOAD_ERR_OK || $ext !== 'zip') {
        $message='Error uploading file.';
    } else {
        $zipFile = $uploaded['tmp_name'];
        $zip = new ZipArchive();
        if ($zip->open($zipFile) !== true) {
            $message='Error uploading file.';
        } elseif ($zip->count() !== 1) {
            $message='Please include a single PDF file in the archive.';
        } else {
            $fileName = $zip->getNameIndex(0);
            if (pathinfo($fileName, PATHINFO_EXTENSION) !== 'pdf') {
                $message='The unzipped file must have a .pdf extension.';
            } elseif (basename($fileName) !== $fileName) {
                $message='Error uploading file.';
            } else {
                $hash = md5_file($zipFile);
                $tmpDir = sys_get_temp_dir().'/zipping-'.$hash;
                $targetDir = __DIR__.'/uploads/'.$hash;
                if (!is_dir($tmpDir)) mkdir($tmpDir, 0700, true);
                // The security flaw is native 7z extraction preserving symlinks
                // combined with publishing them to the web-readable directory.
                exec('7z e -y '.escapeshellarg($zipFile).' -o'.escapeshellarg($tmpDir).' >/dev/null 2>&1', $ignored, $rc);
                $extracted = $tmpDir.'/'.$fileName;
                if ($rc === 0 && file_exists($extracted)) {
                    if (!is_dir($targetDir)) mkdir($targetDir, 0755, true);
                    rename($extracted, $targetDir.'/'.$fileName);
                    $link = '/uploads/'.$hash.'/'.rawurlencode($fileName);
                    $message='Your CV was uploaded successfully.';
                } else {
                    $message='Error uploading file.';
                }
            }
        }
        $zip->close();
    }
}
require_once __DIR__.'/shop/functions.php';
shop_header('Careers');
?>
<section class="hero mini"><p class="eyebrow">CAREERS</p><h1>WORK WITH US.</h1><p>We are always looking for talented people to join our team.</p></section>
<section class="wrap form-wrap"><h2>Send your resume</h2><p>Upload one PDF document inside a ZIP archive to apply.</p>
<?php if ($message): ?><p class="message"><?=htmlspecialchars($message)?> <?php if ($link): ?><a href="<?=htmlspecialchars($link)?>">View uploaded document</a><?php endif; ?></p><?php endif; ?>
<form method="post" enctype="multipart/form-data"><label for="zip_file">ZIP archive (one PDF)</label><input type="file" id="zip_file" name="zip_file" accept=".zip" required><button class="button" type="submit">Submit application</button></form></section>
<?php shop_footer(); ?>
