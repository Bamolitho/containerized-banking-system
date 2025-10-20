#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, jsonify, after_this_request
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, sys, csv, json, tempfile
from datetime import datetime 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../database')))
from database import ensure_db_initialized, get_db_connection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from compte_bancaire import CompteBancaire

app = Flask(__name__)
app.secret_key = '8INF876'

# Instance globale pour gérer les comptes par session
comptes = {}

def get_compte():
    """Récupère ou crée l'instance CompteBancaire pour l'utilisateur connecté"""
    if 'user_id' not in session:
        return None
    
    user_id = session['user_id']
    if user_id not in comptes:
        comptes[user_id] = CompteBancaire()
        # Charger le solde depuis la dernière transaction
        conn = get_db_connection()
        derniere_transaction = conn.execute(
            'SELECT solde FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1',
            (user_id,)
        ).fetchone()
        conn.close()
        
        if derniere_transaction:
            comptes[user_id]._CompteBancaire__solde = derniere_transaction['solde']
    
    return comptes[user_id]


# --- Récupérer les transactions de l'utilisateur connecté ---
def recuperer_transactions():
    if 'user_id' not in session:
        return []
    conn = get_db_connection()
    transactions = conn.execute('''
        SELECT solde, action, montant, timestamp
        FROM transactions
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return [dict(t) for t in transactions]


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
    ensure_db_initialized()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

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
    ensure_db_initialized()
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO users (username, password)
                VALUES (?, ?)
            ''', (username, password))
            conn.commit()
            
            # Récupérer l'ID du nouvel utilisateur
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            
            # Connexion automatique
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            flash("Compte créé avec succès ! Bienvenue.", "success")
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
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

    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) as count FROM transactions WHERE user_id = ?", (session['user_id'],)).fetchone()['count']
    depots = conn.execute("SELECT COUNT(*) as count FROM transactions WHERE user_id = ? AND LOWER(action) = 'depot'", (session['user_id'],)).fetchone()['count']
    retraits = conn.execute("SELECT COUNT(*) as count FROM transactions WHERE user_id = ? AND LOWER(action) = 'retrait'", (session['user_id'],)).fetchone()['count']
    
    solde_actuel = conn.execute("SELECT solde FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (session['user_id'],)).fetchone()
    solde = solde_actuel['solde'] if solde_actuel else 0.0
    
    conn.close()

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
            writer.writerow([t['timestamp'], t['action'], t['montant'], t['solde']])
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
        json.dump(transactions, tmp_file, indent=4, ensure_ascii=False)
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

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

        if not user or not check_password_hash(user['password'], current_password):
            conn.close()
            flash("Mot de passe actuel incorrect.", "error")
            return redirect(url_for('changer_mot_de_passe'))

        conn.execute('UPDATE users SET password = ? WHERE id = ?', (generate_password_hash(new_password), session['user_id']))
        conn.commit()
        conn.close()

        flash("Mot de passe modifié avec succès !", "success")
        return redirect(url_for('index'))

    return render_template('changer_mot_de_passe.html')


# --- SUPPRIMER COMPTE ---
@app.route('/supprimer_compte', methods=['POST'])
def supprimer_compte():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    password = request.form.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if not user or not check_password_hash(user['password'], password):
        conn.close()
        flash("Mot de passe incorrect.", "error")
        return redirect(url_for('index'))
    
    # Suppression du compte (les transactions seront supprimées automatiquement grâce à ON DELETE CASCADE)
    conn.execute('DELETE FROM users WHERE id = ?', (session['user_id'],))
    conn.commit()
    conn.close()

    # Nettoyage de la session
    user_id = session.get('user_id')
    if user_id and user_id in comptes:
        del comptes[user_id]
    
    session.clear()
    flash("Votre compte a bien été supprimé.", "success")
    return redirect(url_for('register'))


# Signaler à Docker que l'application est “vivante
@app.route("/health")
def health():
    return {"status": "ok"}, 200

# --- RUN ---
if __name__ == "__main__":
    ensure_db_initialized()
    app.run(debug=True, host="0.0.0.0", port=6000)
