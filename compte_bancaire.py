#!/usr/bin/env python3

class CompteBancaire:
    def __init__(self):
        self.__liste_identifiants = []
        self.__transactions_record = []
    
    def creerCompte(self):
        nom = input("Votre nom : ")

        if len(self.__liste_identifiants) == 0:
            id = 100000
        else: 
            id = 1 + self.__liste_identifiants[-1]['id']
        
        password = input("Entrez un password : ")

        new = {"nom":nom, "id":id, "password":password}
        self.__liste_identifiants.append(new)

        print(f"Compte créé avec succès. Votre ID est {id}")
        print(self.__liste_identifiants)


    def seConnecter(self, id, password):
        pass

    def consulterCompte(self):
        pass
    
    def deposerArgent(self, montant) :
        if(montant > 0.0) :
            self.__solde += montant
            self.__transactions_record.append(f"Depot de {montant} euros => solde = {self.__solde}")
        else :
            print("Montant doit etre positif")
    
    def retirerArgent(self, montant) :
        if((self.__solde  > montant) & (montant > 0.0)):
            self.__solde -= montant 
            self.__transactions_record.append(f"Retrait de {montant} euros => solde = {self.__solde}")
        elif(montant <= 0.0):
            print("Montant doit etre positif")
        else:
            print("Insufficient funds")
    
    def afficher_historique(self) :
        if self.__transactions_record :
            print("Transactions record : ")
            for transaction in self.__transactions_record:
                print(transaction)
        else:
            print("No transactions yet")
    
    def effacerCompte():
        pass
    
    def __str__ (self) -> str :
        return f"Compte de {self.__nomProprietaire} de solde {self.__solde}"
    

#client1 = CompteBancaire("Amolitho", 2025)
#print(client1) # different de print(client1.__str__)
#client1.afficher_historique()


# client2 = CompteBancaire("BALDE") # Erreur !!! (on doit passer tous les arguments)

#client1.deposer(75)
#print(client1)
#client1.afficher_historique()

#client1.retirer(100)
#print(client1)

#print("\n")
#client1.afficher_historique()

def afficher_menu_non_utilisateur():
    print("\n=== Menu ===")
    print("1. Créer un compte")
    print("2. Se connecter")
    print("0. Quitter")

def afficher_menu_utilisateur():
    print("\n=== Menu ===")
    print("1. Déposer de l'argent")
    print("2. Retirer de l'argent")
    print("3. Consulter compte")
    print("4. Effacer compte")
    print("5. Afficher l'historique des transactions")
    print("0. Quitter")


def get_into_main_menu(compte):
    while True:

        afficher_menu_utilisateur()
        choix = input("Choisissez une option : ")

        if choix == '1':
            montant = float(input("Entrez le montant a deposer : "))
            compte.deposerArgent(montant)
        elif choix == '2':
            montant = float(input("Entrez le montant a retirer : "))
            compte.retirerArgent(montant)
        elif choix == '3':
            compte.consulterCompte()
        elif choix == '4': 
            compte.effacerCompte()
        elif choix == '5':
            compte.afficher_historique()
        elif choix == '0':
            print("Merci d'avoir utilisé notre service bancaire.")
            break
        else:
            print("Choix invalide. Veuillez reessayer.")

def menu():
    compte = CompteBancaire()

    while True:
        afficher_menu_non_utilisateur()
        choix = input("Choisissez une option : ")

        if choix == '1': # Créer compte bancaire
            compte.creerCompte()
        elif choix == '2': # Se connecter
            id = int(input("Votre id : "))
            password = input("Votre password : ")
            status = compte.seConnecter(id, password)
            if status == 200 :
                get_into_main_menu(compte)
            else : 
                print(f"ID ou password incorrect")
        elif choix == '0':
            print("Merci d'avoir utilisé notre service bancaire.")
            break
        else:
            print("Choix invalide. Veuillez reessayer.")

if __name__ == "__main__":
    menu()