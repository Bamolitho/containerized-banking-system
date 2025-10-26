# Structure du répertoire (avant docker compose) : 

```php
containerized-banking-system/
├── .gitignore
├── Dockerfile
├── .dockerignore
│
├── run_gestion_bancaire.sh 	# Construit l'image Docker, lance le conteneur, et ouvre automatiquement le navigateur.			
│
├── README.md
├── structure_repertoire_diagramme_classes.md
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



# Structure du répertoire (après docker compose) : 

```php
containerized-banking-system/
├──compte_bancaire.py # Logique métier : gestion des comptes (créer, déposer, retirer, etc.)
├── docker-compose.yml   # Orchestration des conteneurs : MySQL, Flask et Nginx
├── Makefile             # Commandes automatisées : build, rebuild, logs, clean...
├── README.md            # Documentation du projet (installation, utilisation)
├── .env 				 # Contient les variables d'environnement 
├── run_gestion_bancaire.sh      # Script shell pour exécuter rapidement le projet
├── structure_repertoire_diagramme_classes.md # Description du projet et diagrammes UML / structure
│
├── database/
│   ├── database.py                 # Connexion et exécution des requêtes SQL (MySQL/SQLite)
│   ├── db.db                                # Base de données SQLite locale (tests)
│   ├── init_db.sql                 # Script SQL d’initialisation (création de tables)
│   ├── __init__.py                    # Rend le dossier importable comme module Python
│   └── __pycache__/                         # Fichiers Python compilés (.pyc)
│
├── Images/                                  # Ressources visuelles (captures)
│
├── nginx/
│   └── conf.d/
│       └── default.conf         # Configuration Nginx (reverse proxy vers Flask)
│
└── web/
    ├── app.py               # Application Flask principale (routes, logique serveur)
    ├── compte_bancaire.py    # Version Flask de la logique bancaire (utilisée dans app.py)
    ├── Dockerfile             # Image Docker du service Flask (environnement Python)
    ├── requirements.txt            # Dépendances Python à installer dans le conteneur
    ├── __init__.py                 # Rend le dossier importable comme package Flask
    ├── __pycache__/                         # Cache Python
    │
    │
    ├── static/
    │   └── style.css                        # Feuille de style CSS pour les pages HTML
    │
    └── templates/                           # Pages HTML pour Flask (interface utilisateur)
        ├── changer_mot_de_passe.html       # Page pour modifier le mot de passe utilisateur
        ├── index.html                       # Tableau de bord principal après connexion
        ├── login.html                       # Page de connexion utilisateur
        ├── register.html                    # Page d’inscription utilisateur
        └── stats.html             # Page de statistiques et visualisation des transactions
```