<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>@yield('title', 'Daily Blogs') - Usage</title>
    <style>
        *{box-sizing:border-box}body{margin:0;background:#f5f6f8;color:#30343b;font:15px Arial,sans-serif}
        header{background:#202a35;color:#fff;padding:18px 0}header .inner,main{width:min(980px,92%);margin:auto}
        header a{color:#dce5ed;text-decoration:none;margin-right:20px}.brand{font-weight:700;font-size:21px;margin-right:35px;color:#fff}
        main{padding:48px 0}.card{max-width:470px;margin:0 auto;background:#fff;border:1px solid #e2e5e9;border-radius:6px;padding:30px;box-shadow:0 4px 18px #1d29330d}
        h1{font-size:25px;margin:0 0 8px}.muted{color:#737d88;line-height:1.5;margin-bottom:24px}
        label{display:block;font-weight:600;margin:16px 0 6px}input{width:100%;padding:11px;border:1px solid #cfd5dc;border-radius:4px;font-size:15px}
        button{margin-top:20px;width:100%;padding:12px;border:0;border-radius:4px;background:#2675a8;color:#fff;font-weight:700;cursor:pointer}
        .links{display:flex;justify-content:space-between;margin-top:20px;font-size:13px}.links a{color:#2675a8;text-decoration:none}
        .notice{padding:10px 12px;border-radius:4px;margin:15px 0;background:#edf5fb;color:#24516e}.error{background:#fff0ef;color:#8c2f2a}
        footer{text-align:center;color:#8a929b;font-size:12px;padding:20px}
    </style>
</head>
<body>
<header><div class="inner"><a class="brand" href="http://usage.htb/">Daily Blogs</a><a href="http://usage.htb/">Home</a><a href="http://usage.htb/registration">Register</a><a href="http://admin.usage.htb/">Administration</a></div></header>
<main>@yield('content')</main>
<footer>Daily Blogs · A community publishing platform</footer>
</body>
</html>
