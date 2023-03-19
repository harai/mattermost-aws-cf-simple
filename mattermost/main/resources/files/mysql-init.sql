FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '%%ROOT_PASSWORD%%';
ALTER USER 'root'@'127.0.0.1' IDENTIFIED BY '%%ROOT_PASSWORD%%';
ALTER USER 'root'@'::1' IDENTIFIED BY '%%ROOT_PASSWORD%%';
DELETE FROM mysql.user WHERE user = '';
DELETE FROM mysql.user WHERE host LIKE 'ip-%';
CREATE USER 'mm'@'localhost' IDENTIFIED BY '%%MM_PASSWORD%%';
CREATE DATABASE mm;
GRANT ALL ON mm.* TO 'mm'@'localhost';
FLUSH PRIVILEGES;
