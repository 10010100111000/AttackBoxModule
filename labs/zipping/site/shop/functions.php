<?php
function pdo_connect_mysql() {
    return new PDO(
        'mysql:host=127.0.0.1;port=3306;dbname=zipping;charset=utf8mb4',
        'shop', 'ZippingLocalDbOnly2023!',
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
         PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
         PDO::ATTR_EMULATE_PREPARES => true]
    );
}
function shop_header($title) {
    $safe=htmlspecialchars($title, ENT_QUOTES, 'UTF-8');
    echo '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'.$safe.' - Zipping Watches</title><link rel="stylesheet" href="/assets/style.css"></head><body>';
    echo '<header class="nav"><div class="wrap"><a class="brand" href="/">ZIPPING<span> WATCHES</span></a><nav><a href="/">Home</a><a href="/shop/">Shop</a><a href="/upload.php">Work With Us</a></nav></div></header>';
}
function shop_footer() {
    echo '<footer><div class="wrap">Zipping Watches · Precision in every detail</div></footer></body></html>';
}
