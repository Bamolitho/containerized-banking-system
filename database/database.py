import sqlite3
import os

# Définir le chemin vers la base de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db.db')


# Connexion directe à la DB 
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Création de la table des utilisateurs
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')


# Création de la table transactions, liée à un utilisateur
# action = RETRAIT OU DÉPOT
def init_db_detection():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                solde REAL,
                action TEXT,
                montant REAL,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')


def execute_query(query, params=(), fetch=False):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        if fetch:
            return [dict(row) for row in cur.fetchall()]


# Initialisation automatique des tables
def ensure_db_initialized():
    init_db()
    init_db_detection()


# Appel immédiat à l'importation
ensure_db_initialized()