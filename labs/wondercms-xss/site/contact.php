<?php
/**
 * Public editorial contact form.
 *
 * The submitted website URL is queued for the instance-local review bot.
 * The bot deliberately visits only the URL path on this WonderCMS origin;
 * it never navigates to an arbitrary submitted hostname.
 */
declare(strict_types=1);

$message = '';
$status = 200;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim((string)($_POST['name'] ?? ''));
    $email = trim((string)($_POST['email'] ?? ''));
    $age = trim((string)($_POST['age'] ?? ''));
    $country = trim((string)($_POST['country'] ?? ''));
    $website = trim((string)($_POST['website'] ?? ''));

    $parts = $website !== '' ? parse_url($website) : false;
    $validUrl = is_array($parts)
        && isset($parts['scheme'], $parts['host'])
        && in_array(strtolower($parts['scheme']), ['http', 'https'], true);

    if ($name === '' || strlen($name) > 100
        || !filter_var($email, FILTER_VALIDATE_EMAIL)
        || !preg_match('/^[0-9]{1,3}$/', $age)
        || (int)$age < 1 || (int)$age > 120
        || $country === '' || strlen($country) > 80
        || !$validUrl || strlen($website) > 4096) {
        $status = 400;
        $message = 'Please check the information you entered and try again.';
    } else {
        $queue = '/run/wcms/reports';
        $pending = glob($queue . '/*.json') ?: [];
        if (count($pending) >= 20) {
            $status = 429;
            $message = 'Our editorial team is busy. Please try again later.';
        } else {
            $id = bin2hex(random_bytes(16));
            $record = [
                'id' => $id,
                'name' => $name,
                'email' => $email,
                'age' => (int)$age,
                'country' => $country,
                'website' => $website,
                'created_at' => time(),
            ];
            $tmp = $queue . '/.' . $id . '.tmp';
            $dest = $queue . '/' . $id . '.json';
            $json = json_encode($record, JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR);
            if (file_put_contents($tmp, $json, LOCK_EX) === false) {
                $status = 503;
                $message = 'Your message could not be queued. Please try again.';
            } else {
                chmod($tmp, 0660);
                if (!rename($tmp, $dest)) {
                    @unlink($tmp);
                    $status = 503;
                    $message = 'Your message could not be queued. Please try again.';
                } else {
                    $message = 'Thank you. Your website has been submitted to our editorial team for review.';
                }
            }
        }
    }
}

http_response_code($status);
?><!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Contact · Northbound Press</title>
<style>
:root{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#27343a;background:#f6f8f8}
*{box-sizing:border-box}body{margin:0}.wrap{max-width:760px;margin:64px auto;padding:0 24px}
nav{background:#263238;padding:18px max(calc((100% - 760px)/2),24px);color:#fff}
nav a{color:#fff;text-decoration:none;font-weight:650}
h1{font-size:34px;letter-spacing:-.035em;margin:8px 0 10px}.muted{color:#718087}
form{background:#fff;border:1px solid #e1e7e9;border-radius:8px;padding:26px;margin-top:26px}
label{display:block;font-size:13px;font-weight:650;margin:16px 0 6px}
input{width:100%;padding:11px 12px;border:1px solid #d6dfe2;border-radius:4px;font:inherit}
button{margin-top:22px;border:0;border-radius:4px;background:#2c7897;color:#fff;padding:12px 22px;font:inherit;cursor:pointer}
.notice{padding:13px 16px;background:#e7f3f0;border:1px solid #c9e3dc;border-radius:5px;margin-top:20px}
.error{background:#fff0ee;border-color:#f1cfca}
</style>
</head>
<body>
<nav><a href="/">Northbound Press</a></nav>
<main class="wrap">
<p class="muted">EDITORIAL / CONTACT</p>
<h1>Tell us about your website.</h1>
<p class="muted">We welcome new writers, independent publishers and interesting projects. Send the editorial team your details and a link to your website.</p>
<?php if ($message !== ''): ?>
<div class="notice<?= $status >= 400 ? ' error' : '' ?>"><?= htmlspecialchars($message, ENT_QUOTES, 'UTF-8') ?></div>
<?php endif; ?>
<form method="post" action="/contact.php">
<label for="name">Name</label><input id="name" name="name" maxlength="100" required>
<label for="email">Email</label><input id="email" name="email" type="email" required>
<label for="age">Age</label><input id="age" name="age" inputmode="numeric" required>
<label for="country">Country</label><input id="country" name="country" maxlength="80" required>
<label for="website">Website</label><input id="website" name="website" type="url" placeholder="https://your-website.example/" required>
<button type="submit">Send to editorial</button>
</form>
</main>
</body></html>
