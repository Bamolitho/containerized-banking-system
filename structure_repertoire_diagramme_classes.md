# Structure du répertoire : 

```bash
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

## 