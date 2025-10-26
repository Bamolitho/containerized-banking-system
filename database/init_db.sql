-- =========================================================
-- [INFO] init_db.sql Script d'initialisation de la base de données
-- =========================================================
-- Crée la base de données si elle n'existe pas
CREATE DATABASE IF NOT EXISTS gestion_bancaire
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE gestion_bancaire;

-- =========================================================
-- [INFO] Table: users
-- =========================================================
CREATE TABLE IF NOT EXISTS users (
id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50) NOT NULL UNIQUE,
password VARCHAR(255) NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================
-- [INFO] Table: transactions
-- =========================================================
CREATE TABLE IF NOT EXISTS transactions (
id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT NOT NULL,
solde DECIMAL(10,2),
action ENUM('RETRAIT', 'DEPOT') NOT NULL,
montant DECIMAL(10,2),
timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
INDEX idx_user_id (user_id),
INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT '[OK] Base de données gestion_users initialisée avec succès' AS status;