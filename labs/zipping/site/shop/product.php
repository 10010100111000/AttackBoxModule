<?php
// Faithful Zipping-style regex; dot does not match a newline.
if (isset($_GET['id'])) {
    $id = $_GET['id'];
    // Filtering user input for letters or special characters
    if (preg_match("/^.*[A-Za-z!#$%^&*()\-_=+{}\[\]\\|;:'\",.<>\/?]|[^0-9]$/", $id, $match)) {
        header('Location: index.php');
        exit();
    } else {
        // Real vulnerable MariaDB string concatenation; prepare is not safe when
        // the SQL string already contains attacker-controlled syntax.
        $stmt = $pdo->prepare("SELECT * FROM products WHERE id = '$id'");
        $stmt->execute();
        $product = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!$product) exit('Product does not exist!');
    }
} else {
    exit('No ID provided!');
}
?>
<section class="product"><div class="watch-art">◷</div><div>
<p class="eyebrow">COLLECTION / WATCHES</p>
<h1><?= htmlspecialchars($product['name'], ENT_QUOTES, 'UTF-8') ?></h1>
<p><?= htmlspecialchars($product['description'], ENT_QUOTES, 'UTF-8') ?></p>
<p class="price">$<?= htmlspecialchars((string)$product['price'], ENT_QUOTES, 'UTF-8') ?></p>
<a class="button" href="/shop/">Back to collection</a>
</div></section>
