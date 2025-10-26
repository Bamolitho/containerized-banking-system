#!/bin/bash

# ============================================================
# Script : run_gestion_bancaire.sh
# Description : Construit les images Docker, lance les conteneurs
#               (MySQL, Flask, Nginx), vérifie leur état de santé
#               et ouvre automatiquement le navigateur.
# ============================================================

REVERSE_PROXY_PORT=7500
URL="http://localhost:${REVERSE_PROXY_PORT}/login"
CONTAINER_NAME="gestion_bancaire"

# --- Étape 1 : Nettoyage ---
echo "[INFO] Vérification de l'environnement Docker..."
if ! docker info >/dev/null 2>&1; then
    echo "[ERREUR] Docker n'est pas en cours d'exécution. Démarre Docker et réessaie."
    exit 1
fi

# --- Étape 2 : Construire les images ---
echo "[INFO] Construction des images Docker..."
make build

# --- Étape 3 : Lancer les conteneurs ---
echo "[INFO] Démarrage des conteneurs..."
make up

# --- Étape 4 : Attente du démarrage complet ---
echo "[INFO] Attente du démarrage de l'application (10 secondes)..."
sleep 10

# --- Étape 5 : Vérification de la santé du conteneur principal ---
echo "[INFO] Vérification de l'état du conteneur '$CONTAINER_NAME'..."
HEALTH=$(sudo docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null)

if [ -z "$HEALTH" ]; then
    echo "[ERREUR] Impossible de récupérer l'état du conteneur '$CONTAINER_NAME'."
    sudo docker ps
    exit 1
fi

if [ "$HEALTH" = "healthy" ]; then
    echo "[OK] L'application Flask est en bon état (healthy)."
elif [ "$HEALTH" = "unhealthy" ]; then
    echo "[AVERTISSEMENT] L'application est en état UNHEALTHY. Consulte les logs :"
    echo "sudo docker logs $CONTAINER_NAME"
else
    echo "[INFO] État du conteneur : $HEALTH"
fi

# --- Étape 6 : Affichage des conteneurs actifs ---
echo
echo "[INFO] État actuel des conteneurs :"
sudo docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

# --- Étape 7 : Ouverture du navigateur ---
echo
echo "[INFO] Ouverture du navigateur sur $URL ..."
if command -v xdg-open &> /dev/null; then
    xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open &> /dev/null; then
    open "$URL" >/dev/null 2>&1 &
else
    echo "[AVERTISSEMENT] Impossible d'ouvrir automatiquement le navigateur."
    echo "Ouvre manuellement : $URL"
fi

echo
echo "[OK] Système de gestion bancaire prêt à l'emploi."