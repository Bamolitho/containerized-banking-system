Application bancaire containérizé qui permet à un utilisateur de : créer, consulter ou effacer un compte, déposer ou rétirer de l'argent. 



Application bancaire qui permet de créer ou supprimer un compte et réaliser des transactions

​    Paramètres clés à utiliser pour se connecter à un compte : 
        - Un id unique de 6 chiffres (généré par le système)
                - Et un mot de passe (choisi par l'usager)
        
        - Une base de données SQLite pour stocker les infos principales
            - Utilisation de Flask, HTML / CSS / JS  pour créer une interface web

# Structure du répertoire : 

containerized-banking-system/
├── .gitignore
├── Dockerfile
├── db.db 		# sera créée automatiquement
├
├── compte_bancaire.py     # Contient la classe principale et les méthodes creerCompte(), deposerArgent()...  
├
├── app.py
├
├── README.md          
├── requirements.txt  # Les librairies Python utilisés, aucune installation nécessaire
└── web/              # Répertoire des fichiers pour l'interface web 

​	├── style.css

​	├── style.js

​        └── index.html    # Page d'accueil par défaut
   