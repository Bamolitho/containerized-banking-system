#!/usr/bin/env python3

import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './database')))
from database import execute_query


class CompteBancaire:
    def __init__(self):
        self.__solde = 0.0

    def creerCompte(self):
        nom = input("Votre nom : ")
        password = input("Entrez un password : ")

        query = "INSERT INTO users (username, password) VALUES (?, ?)"
        execute_query(query, (nom, password))

        # Récupération de l’ID du compte créé
        result = execute_query("SELECT id FROM users WHERE username = ?", (nom,), fetch=True)
        user_id = result[0]["id"]

        print(f"Compte créé avec succès. Votre ID est {user_id} et votre mot de passe est {password}")
        return user_id, password

    def seConnecter(self, id, password):
        query = "SELECT * FROM users WHERE id = ? AND password = ?"
        result = execute_query(query, (id, password), fetch=True)
        return 200 if result else 404

    def consulterCompte(self):
        print(f"Solde actuel : {self.__solde} €")

    def deposerArgent(self, montant, user_id):
        if montant > 0.0:
            self.__solde += montant
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            execute_query("""
                INSERT INTO transactions (user_id, solde, action, montant, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, self.__solde, "DEPOT", montant, now))

            print(f"Dépôt de {montant} € effectué. Nouveau solde : {self.__solde} €")
        else:
            print("Montant invalide. Le montant doit être positif.")

    def retirerArgent(self, montant, user_id):
        if montant <= 0:
            print("Montant invalide. Le montant doit être positif.")
            return

        if montant > self.__solde:
            print("Fonds insuffisants.")
            return

        self.__solde -= montant
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        execute_query("""
            INSERT INTO transactions (user_id, solde, action, montant, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, self.__solde, "RETRAIT", montant, now))

        print(f"Retrait de {montant} € effectué. Nouveau solde : {self.__solde} €")

    def afficher_historique(self, user_id):
        result = execute_query("SELECT * FROM transactions WHERE user_id = ?", (user_id,), fetch=True)

        if not result:
            print("Aucune transaction enregistrée.")
            return

        print("\n=== Historique des transactions ===")
        for row in result:
            print(f"[{row['timestamp']}] {row['action']} de {row['montant']} € — solde : {row['solde']} €")
        print("===================================")

    def effacerCompte(self, id, password):
        result = execute_query("SELECT * FROM users WHERE id = ? AND password = ?", (id, password), fetch=True)
        if not result:
            return 404

        confirmation = input("Confirmez la suppression du compte (o/n) : ")
        if confirmation.lower() == "o":
            execute_query("DELETE FROM users WHERE id = ?", (id,))
            print("Compte supprimé avec succès.")
            return 200
        else:
            print("Suppression annulée.")
            return 403


class MenuBancaire:
    def afficher_menu_non_utilisateur(self):
        print("\n=== MENU PRINCIPAL ===")
        print("1. Créer un compte")
        print("2. Se connecter")
        print("0. Quitter")

    def afficher_menu_utilisateur(self):
        print("\n=== MENU UTILISATEUR ===")
        print("1. Déposer de l'argent")
        print("2. Retirer de l'argent")
        print("3. Consulter le compte")
        print("4. Effacer le compte")
        print("5. Afficher l'historique des transactions")
        print("0. Se déconnecter")

    def get_into_main_menu(self, compte, user_id):
        while True:
            self.afficher_menu_utilisateur()
            choix = input("Choisissez une option : ")

            if choix == '1':  # Dépôt
                montant = float(input("Entrez le montant à déposer : "))
                compte.deposerArgent(montant, user_id)

            elif choix == '2':  # Retrait
                montant = float(input("Entrez le montant à retirer : "))
                compte.retirerArgent(montant, user_id)

            elif choix == '3':  # Consulter compte
                compte.consulterCompte()

            elif choix == '4':  # Effacer compte
                print("[!] Cette action est irréversible.")
                id = int(input("Entrez votre ID : "))
                password = input("Entrez votre mot de passe : ")
                status = compte.effacerCompte(id, password)
                if status == 200:
                    break

            elif choix == '5':  # Historique
                compte.afficher_historique(user_id)

            elif choix == '0':  # Déconnexion
                print("Déconnexion réussie.")
                break

            else:
                print("Choix invalide. Réessayez.")

    def menu(self):
        compte = CompteBancaire()

        while True:
            self.afficher_menu_non_utilisateur()
            choix = input("Choisissez une option : ")

            if choix == '1':  # Créer un compte
                user_id, password = compte.creerCompte()
                self.get_into_main_menu(compte, user_id)

            elif choix == '2':  # Se connecter
                id = int(input("Entrez votre ID : "))
                password = input("Entrez votre mot de passe : ")
                status = compte.seConnecter(id, password)
                if status == 200:
                    self.get_into_main_menu(compte, id)
                else:
                    print("Identifiants incorrects. Connexion échouée.")

            elif choix == '0':
                print("Merci d'avoir utilisé notre service bancaire.")
                break

            else:
                print("Choix invalide. Réessayez.")


if __name__ == "__main__":
    menu_bancaire = MenuBancaire()
    menu_bancaire.menu()
