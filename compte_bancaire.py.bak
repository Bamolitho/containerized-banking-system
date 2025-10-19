#!/usr/bin/env python3

from datetime import datetime

class CompteBancaire:
    def __init__(self):
        self.__liste_identifiants = []
        self.__transactions_record = []
        self.__solde = 0.0
    
    def creerCompte(self):
        nom = input("Votre nom : ")

        if len(self.__liste_identifiants) == 0:
            id = 100000
        else: 
            id = 1 + self.__liste_identifiants[-1]['id']
        
        password = input("Entrez un password : ")

        new = {"nom":nom, "id":id, "password":password}
        self.__liste_identifiants.append(new)

        return id, password

    def seConnecter(self, id, password):
        for i in range(len(self.__liste_identifiants)) :
            if id == self.__liste_identifiants[i]['id'] and password == self.__liste_identifiants[i]["password"]:
                return 200
        return 404

    def consulterCompte(self):
        print(f"Solde actuel : {self.__solde}")
    
    def deposerArgent(self, montant) :
        if(montant > 0.0) :
            self.__solde += montant
            self.__transactions_record.append(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Depot de {montant} euros => solde = {self.__solde}"
                )
        else :
            print("Montant doit être positif")
    
    def retirerArgent(self, montant) :
        if((self.__solde  > montant) & (montant > 0.0)):
            self.__solde -= montant 
            self.__transactions_record.append(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Retrait de {montant} euros => solde = {self.__solde}"
                )
        elif(montant <= 0.0):
            print("Montant doit être positif")
        else:
            print("Insufficient funds")
    
    def afficher_historique(self) :
        if self.__transactions_record :
            print("\n====================== Historique des transactions ========================")
            for transaction in self.__transactions_record:
                print(f"• {transaction}")
            print("============================================================================")
        else:
            print("No transactions yet")
    
    def effacerCompte(self, id, password):
        for compte in self.__liste_identifiants:
            if compte["id"] == id and compte["password"] == password:
                confirmation = input("Confirmez la suppression (o/n) : ")
                if confirmation.lower() == "o":
                    self.__liste_identifiants.remove(compte)
                    return 200
                else:
                    return 403
        return 404

    
    # def __str__ (self) -> str :
    #     return f"Compte de {self.__nomProprietaire} de solde {self.__solde}"

class MenuBancaire:
    def afficher_menu_non_utilisateur(self):
        print("\n=== Menu ===")
        print("1. Créer un compte")
        print("2. Se connecter")
        print("0. Quitter")

    def afficher_menu_utilisateur(self):
        print("\n=== Menu ===")
        print("1. Déposer de l'argent")
        print("2. Retirer de l'argent")
        print("3. Consulter compte")
        print("4. Effacer compte")
        print("5. Afficher l'historique des transactions")
        print("0. Se déconnecter")


    def get_into_main_menu(self, compte):
        while True:

            self.afficher_menu_utilisateur()
            choix = input("Choisissez une option : ")

            if choix == '1': # Déposer argent
                montant = float(input("Entrez le montant a deposer : "))
                compte.deposerArgent(montant)

            elif choix == '2': # Rétirer argent
                montant = float(input("Entrez le montant a retirer : "))
                compte.retirerArgent(montant)

            elif choix == '3': # Consulter compte
                compte.consulterCompte()

            elif choix == '4': # Effacer compte
                print(f"[!] Cette action est irréversible")
                id = int(input("Entrez votre ID : "))
                password = input("Entrez votre password : ")
                status = compte.effacerCompte(id, password)
                if status == 200 :
                    print(f"Compte {id} supprimé avec succès.")
                    break
                elif status == 403 : 
                    print("Suppression annulée.")
                else : 
                    print("Identifiants incorrects. Suppression échouée.")

            elif choix == '5': # Afficher historique
                compte.afficher_historique()

            elif choix == '0': # Se déconnecter
                print("Merci d'avoir utilisé notre service bancaire.")
                break

            else:
                print("Choix invalide. Veuillez reessayer.")

    def menu(self):
        compte = CompteBancaire()

        while True:
            self.afficher_menu_non_utilisateur()
            choix = input("Choisissez une option : ")

            if choix == '1': # Créer compte bancaire
                id, password = compte.creerCompte()
                print(f"Compte créé avec succès. Votre ID est {id} et password = {password}")
                self.get_into_main_menu(compte)

            elif choix == '2': # Se connecter
                id = int(input("Votre ID : "))
                password = input("Votre password : ")
                status = compte.seConnecter(id, password)
                if status == 200 :
                    self.get_into_main_menu(compte)
                else : 
                    print("Identifiants incorrects. Connexion échouée.")

            elif choix == '0': # Quitter
                print("Merci d'avoir utilisé notre service bancaire.")
                break

            else:
                print("Choix invalide. Veuillez reessayer.")

if __name__ == "__main__":
    menu_bancaire = MenuBancaire()
    menu_bancaire.menu()