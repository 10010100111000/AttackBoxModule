CREATE DATABASE IF NOT EXISTS zipping;
CREATE USER IF NOT EXISTS 'shop'@'127.0.0.1' IDENTIFIED BY 'ZippingLocalDbOnly2023!';
GRANT SELECT ON zipping.* TO 'shop'@'127.0.0.1';
GRANT FILE ON *.* TO 'shop'@'127.0.0.1';
USE zipping;
CREATE TABLE IF NOT EXISTS products (
 id INT PRIMARY KEY, name VARCHAR(160), description TEXT,
 price DECIMAL(10,2), rrp DECIMAL(10,2),
 quantity INT, img VARCHAR(100), date_added DATETIME
);
INSERT IGNORE INTO products VALUES
 (1,'Classic Leather','A timeless watch with polished details.',189.00,249.00,12,'classic',NOW()),
 (2,'Sport Chronograph','Built for everyday routines.',249.00,329.00,8,'sport',NOW()),
 (3,'Minimal Silver','An understated contemporary finish.',139.00,179.00,16,'silver',NOW()),
 (4,'Heritage Gold','A refined metal watch.',299.00,389.00,6,'gold',NOW());
FLUSH PRIVILEGES;
