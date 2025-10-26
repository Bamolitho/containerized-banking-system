#!/usr/bin/env python3

import sys, os
# --- Ajouter le dossier parent au PYTHONPATH ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Imports standards ---
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, jsonify, after_this_request
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import csv, json, tempfile
from datetime import datetime
from decimal import Decimal

# --- Imports locaux ---
from compte_bancaire import CompteBancaire
from database import database

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret')

# Configuration MySQL
app.config['MYSQL_HOST'] = os.getenv('DB_HOST', 'db')
app.config['MYSQL_USER'] = os.getenv('DB_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('DB_NAME', 'gestion_bancaire')
app.config['MYSQL_CHARSET'] = 'utf8mb4'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', '3306'))

mysql = MySQL(app)

# Initialiser la connexion MySQL dans database.py
database.init_mysql(mysql)

# Instance globale pour gérer les comptes par session
comptes = {}

def convert_decimal(obj):
    """Convertit les objets Decimal en float pour la sérialisation JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal(item) for item in obj]
    return obj

def get_compte():
    """Récupère ou crée l'instance CompteBancaire pour l'utilisateur connecté"""
    if 'user_id' not in session:
        return None
    
    user_id = session['user_id']
    if user_id not in comptes:
        comptes[user_id] = CompteBancaire()
        # Charger le solde depuis la dernière transaction
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            'SELECT solde FROM transactions WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1',
            (user_id,)
        )
        derniere_transaction = cur.fetchone()
        cur.close()
        
        if derniere_transaction:
            comptes[user_id]._CompteBancaire__solde = float(derniere_transaction['solde'])
    
    return comptes[user_id]


# --- Récupérer les transactions de l'utilisateur connecté ---
def recuperer_transactions():
    if 'user_id' not in session:
        return []
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''
        SELECT solde, action, montant, timestamp
        FROM transactions
        WHERE user_id = %s
        ORDER BY timestamp DESC
    ''', (session['user_id'],))
    transactions = cur.fetchall()
    cur.close()
    # Convertir les Decimal en float pour la sérialisation JSON
    return [convert_decimal(dict(t)) for t in transactions]


# --- Route JSON temps réel ---
@app.route('/transactions_json')
def transactions_json():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(recuperer_transactions())


# --- ACCUEIL ---
@app.route("/")
def accueil():
    return redirect(url_for('login'))


# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Connexion réussie !", "success")
            return redirect(url_for('index'))

        flash("Nom d'utilisateur ou mot de passe incorrect.", "error")

    return render_template('login.html')


# --- REGISTER ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('''
                INSERT INTO users (username, password)
                VALUES (%s, %s)
            ''', (username, password))
            mysql.connection.commit()
            
            # Récupérer l'ID du nouvel utilisateur
            cur.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cur.fetchone()
            cur.close()
            
            # Connexion automatique
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            flash("Compte créé avec succès ! Bienvenue.", "success")
            return redirect(url_for('index'))
        except MySQLdb.IntegrityError:
            flash("Nom d'utilisateur déjà pris.", "error")

    return render_template('register.html')


# --- LOGOUT ---
@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id and user_id in comptes:
        del comptes[user_id]
    session.clear()
    flash("Déconnecté avec succès.", "success")
    return redirect(url_for('login'))


# --- INDEX (transactions) ---
@app.route("/index")
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    compte = get_compte()
    transactions = recuperer_transactions()
    stats = calculer_stats(render=False)
    
    return render_template("index.html", 
                         transactions=transactions, 
                         stats=stats,
                         solde_actuel=compte._CompteBancaire__solde if compte else 0.0)


# --- DEPOT ---
@app.route('/depot', methods=['POST'])
def depot():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        montant = float(request.form['montant'])
        compte = get_compte()
        
        if montant <= 0:
            flash("Le montant doit être positif.", "error")
        else:
            compte.deposerArgent(montant, session['user_id'])
            flash(f"Dépôt de {montant:.2f} € effectué avec succès.", "success")
    except ValueError:
        flash("Montant invalide.", "error")
    
    return redirect(url_for('index'))


# --- RETRAIT ---
@app.route('/retrait', methods=['POST'])
def retrait():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        montant = float(request.form['montant'])
        compte = get_compte()
        
        if montant <= 0:
            flash("Le montant doit être positif.", "error")
        elif montant > compte._CompteBancaire__solde:
            flash("Fonds insuffisants.", "error")
        else:
            compte.retirerArgent(montant, session['user_id'])
            flash(f"Retrait de {montant:.2f} € effectué avec succès.", "success")
    except ValueError:
        flash("Montant invalide.", "error")
    
    return redirect(url_for('index'))


# --- STATS ---
@app.route("/stats")
def calculer_stats(render=True):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cur.execute("SELECT COUNT(*) as count FROM transactions WHERE user_id = %s", (session['user_id'],))
    total = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM transactions WHERE user_id = %s AND LOWER(action) = 'depot'", (session['user_id'],))
    depots = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM transactions WHERE user_id = %s AND LOWER(action) = 'retrait'", (session['user_id'],))
    retraits = cur.fetchone()['count']
    
    cur.execute("SELECT solde FROM transactions WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1", (session['user_id'],))
    solde_actuel = cur.fetchone()
    solde = float(solde_actuel['solde']) if solde_actuel else 0.0
    
    cur.close()

    stats = {
        'total': total,
        'depots': depots,
        'retraits': retraits,
        'solde': round(solde, 2)
    }

    if render:
        return render_template('stats.html', stats=stats)
    else:
        return stats


# --- EXPORT CSV ---
@app.route('/export_csv')
def export_csv():
    if 'user_id' not in session:
        flash("Connexion requise.", "error")
        return redirect(url_for('login'))

    transactions = recuperer_transactions()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='', encoding='utf-8')
    try:
        writer = csv.writer(tmp_file)
        writer.writerow(['Timestamp', 'Action', 'Montant', 'Solde'])
        for t in transactions:
            # Convertir Decimal en float si nécessaire (déjà fait par recuperer_transactions)
            montant = float(t['montant']) if isinstance(t['montant'], Decimal) else t['montant']
            solde = float(t['solde']) if isinstance(t['solde'], Decimal) else t['solde']
            writer.writerow([t['timestamp'], t['action'], montant, solde])
    finally:
        tmp_file.close()

    @after_this_request
    def remove_file(response):
        try:
            os.remove(tmp_file.name)
        except Exception as e:
            print(f"Erreur suppression fichier temporaire : {e}")
        return response

    return send_file(tmp_file.name, as_attachment=True, download_name='export_transactions.csv')


# --- EXPORT JSON ---
@app.route('/export_json')
def export_json():
    if 'user_id' not in session:
        flash("Connexion requise.", "error")
        return redirect(url_for('login'))

    transactions = recuperer_transactions()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w', encoding='utf-8')
    try:
        # Les transactions sont déjà converties par recuperer_transactions()
        # Ajout de default=str pour une sécurité supplémentaire
        json.dump(transactions, tmp_file, indent=4, ensure_ascii=False, default=str)
    finally:
        tmp_file.close()

    @after_this_request
    def remove_file(response):
        try:
            os.remove(tmp_file.name)
        except Exception as e:
            print(f"Erreur suppression fichier : {e}")
        return response

    return send_file(tmp_file.name, as_attachment=True, download_name='export_transactions.json')


# --- CHANGER MOT DE PASSE ---
@app.route('/changer-mot-de-passe', methods=['GET', 'POST'])
def changer_mot_de_passe():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            flash("Merci de remplir tous les champs.", "error")
            return redirect(url_for('changer_mot_de_passe'))

        if new_password != confirm_password:
            flash("Le nouveau mot de passe et la confirmation ne correspondent pas.", "error")
            return redirect(url_for('changer_mot_de_passe'))

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
        user = cur.fetchone()

        if not user or not check_password_hash(user['password'], current_password):
            cur.close()
            flash("Mot de passe actuel incorrect.", "error")
            return redirect(url_for('changer_mot_de_passe'))

        cur.execute('UPDATE users SET password = %s WHERE id = %s', (generate_password_hash(new_password), session['user_id']))
        mysql.connection.commit()
        cur.close()

        flash("Mot de passe modifié avec succès !", "success")
        return redirect(url_for('index'))

    return render_template('changer_mot_de_passe.html')


# --- SUPPRIMER COMPTE ---
@app.route('/supprimer_compte', methods=['POST'])
def supprimer_compte():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    password = request.form.get('password')
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cur.fetchone()
    
    if not user or not check_password_hash(user['password'], password):
        cur.close()
        flash("Mot de passe incorrect.", "error")
        return redirect(url_for('index'))
    
    # Suppression du compte (les transactions seront supprimées automatiquement grâce à ON DELETE CASCADE)
    cur.execute('DELETE FROM users WHERE id = %s', (session['user_id'],))
    mysql.connection.commit()
    cur.close()

    # Nettoyage de la session
    user_id = session.get('user_id')
    if user_id and user_id in comptes:
        del comptes[user_id]
    
    session.clear()
    flash("Votre compte a bien été supprimé.", "success")
    return redirect(url_for('register'))


# Signaler à Docker que l'application est "vivante
@app.route("/health")
def health():
    return {"status": "ok"}, 200

# --- RUN ---
if __name__ == "__main__":
    # Attendre que MySQL soit prêt (utile dans Docker)
    import time
    import MySQLdb
    max_retries = 30
    retry_count = 0
    
    print("[WAIT] Attente de la disponibilité de MySQL...")
    
    while retry_count < max_retries:
        try:
            # Tester la connexion directement avec MySQLdb (pas besoin de contexte Flask)
            test_conn = MySQLdb.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                db=app.config['MYSQL_DB'],
                port=app.config['MYSQL_PORT']
            )
            test_conn.close()
            print("[SUCCESS] Connexion MySQL établie avec succès")
            break
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                print(f"[WAIT] Attente de MySQL... tentative {retry_count}/{max_retries}")
                time.sleep(2)
            else:
                print(f"[FAILED] Impossible de se connecter à MySQL après {max_retries} tentatives")
                print(f"Erreur: {e}")
                raise e
    
    # Initialiser les tables dans un contexte Flask
    with app.app_context():
        database.ensure_db_initialized()
        print("[SUCCESS] Tables initialisées")
    
    print("[RUNNING] Démarrage de l'application Flask...")
    app.run(debug=True, host="0.0.0.0", port=5500)