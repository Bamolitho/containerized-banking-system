#!/bin/bash

echo " Lancement du système de gestion bancaire..."

# Dossier racine du projet (à adapter si besoin)
PROJECT_DIR="$(pwd)"

# Lancement de l'application Flask (app.py)
gnome-terminal --title="🌐 App Flask" -- bash -c "
cd \"$PROJECT_DIR/web\"
echo 'Lancement de l''application Flask...'
python3 app.py
exec bash"

# Ouvrir le navigateur automatiquement
if command -v xdg-open &> /dev/null; then
    echo "🌐 Ouverture du navigateur..."
    sleep 1
    xdg-open "http://localhost:5003/login" 2>/dev/null &
fi

echo "Système prêt à l'emploi !"