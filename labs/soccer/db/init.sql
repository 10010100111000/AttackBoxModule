CREATE DATABASE IF NOT EXISTS soccer_db;
CREATE USER IF NOT EXISTS 'ticket_reader'@'127.0.0.1' IDENTIFIED BY 'ticket_reader_pass';
GRANT SELECT ON soccer_db.* TO 'ticket_reader'@'127.0.0.1';
USE soccer_db;
CREATE TABLE IF NOT EXISTS tickets (id INT PRIMARY KEY, event_name VARCHAR(100) NOT NULL);
CREATE TABLE IF NOT EXISTS accounts (id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(50), password VARCHAR(120), email VARCHAR(100), goal VARCHAR(100) NOT NULL DEFAULT '');
INSERT IGNORE INTO tickets VALUES (86881, 'City Cup Final'),(86882,'Derby Night'),(86883,'Junior League');
INSERT IGNORE INTO accounts (id,username,password,email) VALUES (1,'player','PlayerOftheMatch2022','player@player.htb');
