<?php
session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: /login/login.php');
    exit;
}

$message = '';
$messageType = 'success';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!isset($_FILES['upload']) || $_FILES['upload']['error'] !== UPLOAD_ERR_OK) {
        $message = 'Please select a file to upload.';
        $messageType = 'danger';
    } else {
        // Deliberately vulnerable: no file type, extension, or content validation.
        $uploadDirectory = __DIR__ . '/_uploaded/';
        $fileName = basename($_FILES['upload']['name']);
        $destination = $uploadDirectory . $fileName;

        if (move_uploaded_file($_FILES['upload']['tmp_name'], $destination)) {
            $message = 'Your file has been uploaded successfully.';
        } else {
            $message = 'The file could not be uploaded.';
            $messageType = 'danger';
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Admin File Uploads - BASE</title>
  <link rel="icon" href="/assets/img/favicon.png">
  <link rel="stylesheet" href="/assets/vendor/bootstrap/css/bootstrap.min.css">
  <link rel="stylesheet" href="/assets/vendor/bootstrap-icons/bootstrap-icons.css">
  <link rel="stylesheet" href="/assets/css/base-pages.css">
</head>
<body class="base-upload-page">
  <div class="base-upload-shell">
    <header class="base-upload-header">
      <span>Admin File Uploads</span>
      <a href="/logout.php" class="btn btn-light btn-sm"><i class="bi bi-box-arrow-right"></i> LOG OUT</a>
    </header>

    <main class="base-upload-main">
      <div class="base-upload-content">
        <i class="bi bi-cloud-fill base-upload-cloud" aria-hidden="true"></i>
        <h1>Upload Your <strong>Files</strong> To Base Server</h1>
        <?php if ($message !== ''): ?>
          <div class="alert alert-<?php echo $messageType; ?>" role="alert"><?php echo htmlspecialchars($message, ENT_QUOTES, 'UTF-8'); ?></div>
        <?php endif; ?>
        <form id="upload-form" method="POST" enctype="multipart/form-data">
          <input id="upload-file" class="visually-hidden" type="file" name="upload" required>
          <label class="base-upload-button" for="upload-file">SELECT YOUR UPLOAD</label>
          <noscript><button class="base-upload-button" type="submit">UPLOAD FILE</button></noscript>
        </form>
      </div>
    </main>

    <footer class="base-upload-footer">&copy; BASE. ALL RIGHTS RESERVED.</footer>
  </div>
  <script>
    document.getElementById('upload-file').addEventListener('change', function () {
      if (this.files && this.files.length) {
        document.getElementById('upload-form').submit();
      }
    });
  </script>
</body>
</html>
