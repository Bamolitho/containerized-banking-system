# Implémentation HTTP avec Sockets Python



## Objectifs

Application bancaire containérizé qui permet à un utilisateur de : créer, consulter ou effacer un compte, déposer ou rétirer de l'argent. 



Application bancaire qui permet de créer ou supprimer un compte et réaliser des transactions

​    Paramètres clés à utiliser pour se connecter à un compte : 
   - Un id unique de 6 chiffres (généré par le système)
   - un mot de passe (choisi par l'usager)

- Une base de données SQLite pour stocker les infos principales
- Utilisation de Flask, HTML / CSS / JS  pour créer une interface web

# Structure du répertoire : 

```bash
containerized-banking-system/
├── .gitignore
├── Dockerfile
│
├── README.md
├── requirements.txt			# Librairies Python nécessaires (aucune installation manuelle requise)
├── compte_bancaire.py          # Classe principale avec les fonctions creerCompte(), deposerArgent(), etc.
├── database/
│   ├── database.py             # Adapté avec PRAGMA foreign_keys
│   └── db.db                   # Base de données SQLite (créée automatiquement)
└── web/						# Fichiers pour l’interface web
    ├── app.py                  # Application Flask avec toutes les routes
    ├── templates/
    │   ├── index.html          # Page d'accueil avec actions
    │   ├── login.html
    │   ├── register.html
    │   ├── changer_mot_de_passe.html
    │   └── stats.html
    └── static/
        └── style.css
```

## Installation et lancement

### Prérequis

- Python 3.6+ (aucune dépendance externe)
- Système d'exploitation : Windows, Linux, macOS

### Installation

```
# 1. 
```



## Utilisation

### 1. 

```
# 
```



**Sortie attendue :**

```
============================================================
[INFO] 
```

### 2. 

```

```

# Scénario de test complet



# Diagramme de classes

```basic
+---------------------------+
|    CompteBancaire         |
+---------------------------+
| - __liste_identifiants    |
| - __transactions_record   |
| - __solde                 |
+---------------------------+
| + creerCompte()           |
| + seConnecter()           |
| + consulterCompte()       |
| + deposerArgent()         |
| + retirerArgent()         |
| + afficher_historique()   |
| + effacerCompte()         |
+---------------------------+
        ▲
        │ uses
        │
+---------------------------+
|    MenuBancaire           |
+---------------------------+
| + afficher_menu_non_utilisateur() |
| + afficher_menu_utilisateur()     |
| + get_into_main_menu()            |
| + menu()                          |
+-----------------------------------+
```

MenuBancaire utilise un objet CompteBancaire

### Relations (simplifiées)

```basic
main()
  └──> menu()
        ├──> afficher_menu_non_utilisateur()
        ├──> [Choix utilisateur]
        │     ├── (1) creerCompte()
        │     ├── (2) seConnecter(id, password)
        │     │       └──> get_into_main_menu()
        │     │             ├──> afficher_menu_utilisateur()
        │     │             ├── [Choix utilisateur]
        │     │             │     ├── (1) deposerArgent()
        │     │             │     ├── (2) retirerArgent()
        │     │             │     ├── (3) consulterCompte()
        │     │             │     ├── (4) effacerCompte(id, password)
        │     │             │     └── (5) afficher_historique()
        │     │             └──> retour au menu principal
        │     └── (0) Quitter le programme
        └──> Fin du programme
```

## Références

Scripts et logique web : https://github.com/Bamolitho/phishing-detection-ml/tree/main