<?php $products=$pdo->query('SELECT id,name,description,price FROM products ORDER BY id')->fetchAll(); ?>
<div class="hero mini"><p class="eyebrow">THE COLLECTION</p><h1>TIME IS EVERYTHING.</h1><p>Explore classic watches crafted for daily life.</p></div>
<section class="wrap"><div class="grid">
<?php foreach ($products as $p): ?>
<article class="watch-card"><div class="watch-art">◷</div><h2><?=htmlspecialchars($p['name'])?></h2><p><?=htmlspecialchars($p['description'])?></p><p class="price">$<?=htmlspecialchars($p['price'])?></p>
<a href="/shop/index.php?page=product&amp;id=<?=$p['id']?>">View details</a></article>
<?php endforeach; ?>
</div></section>
