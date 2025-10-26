# database.py
import MySQLdb.cursors
import os

# Cette variable sera initialisée par app.py
mysql_instance = None

def init_mysql(mysql):
    """Initialise la connexion MySQL depuis Flask"""
    global mysql_instance
    mysql_instance = mysql


# Connexion directe à la DB 
def get_db_connection():
    """Retourne la connexion MySQL depuis Flask-MySQLdb"""
    if mysql_instance is None:
        raise RuntimeError("MySQL n'est pas initialisé. Appelez init_mysql() depuis app.py")
    return mysql_instance.connection


# Création de la table des utilisateurs
def init_db():
    try:
        cur = mysql_instance.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        mysql_instance.connection.commit()
        cur.close()
    except Exception as e:
        print(f"Erreur lors de la création de la table users: {e}")


# Création de la table transactions, liée à un utilisateur
# action = RETRAIT OU DÉPOT
def init_db_detection():
    try:
        cur = mysql_instance.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''')
        mysql_instance.connection.commit()
        cur.close()
    except Exception as e:
        print(f"Erreur lors de la création de la table transactions: {e}")


def execute_query(query, params=(), fetch=False):
    if mysql_instance is None:
        return [] if fetch else None
    
    try:
        cur = mysql_instance.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(query, params)
        mysql_instance.connection.commit()
        if fetch:
            result = cur.fetchall()
            cur.close()
            return result
        cur.close()
    except Exception as e:
        print(f"Erreur lors de l'exécution de la requête: {e}")
        return [] if fetch else None


# Initialisation automatique des tables
def ensure_db_initialized():
    if mysql_instance is not None:
        init_db()
        init_db_detection()