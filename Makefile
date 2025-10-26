# [INFO] Makefile pour simplifier les commandes Docker Compose
.PHONY: help build up down restart logs clean test backup

# Couleurs pour les messages
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m

help: ## [INFO] Afficher l'aide
	@echo "$(GREEN)[INFO] Commandes disponibles:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

build: ## [INFO] Construire les images Docker
	@echo "$(GREEN)[INFO] Construction des images...$(NC)"
	docker compose build

up: ## [OK] Démarrer tous les services
	@echo "$(GREEN)[OK] Démarrage des services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)[OK] Services démarrés!$(NC)"
	@echo "$(YELLOW)[INFO] Application disponible sur:$(NC)"
	@echo "  - http://localhost:7500 (via Nginx)"
	@echo "  - http://localhost:5500 (Flask direct)"

launch:
	@echo "  - http://localhost:7500 (via Nginx)"
	@echo "  - http://localhost:5500 (Flask direct)"

down: ## [INFO] Arrêter tous les services
	@echo "$(YELLOW)[INFO] Arrêt des services...$(NC)"
	docker compose down

restart: ## [INFO] Redémarrer tous les services
	@echo "$(YELLOW)[INFO] Redémarrage des services...$(NC)"
	docker compose restart

logs: ## [INFO] Afficher les logs en temps réel
	docker compose logs -f

logs-app: ## [INFO] Logs de l'application Flask uniquement
	docker compose logs -f app

logs-db: ## [INFO] Logs de MySQL uniquement
	docker compose logs -f db

logs-nginx: ## [INFO] Logs de Nginx uniquement
	docker compose logs -f nginx

status: ## [INFO] Vérifier l'état des services
	@echo "$(GREEN)[INFO] État des services:$(NC)"
	docker compose ps

shell-app: ## [INFO] Ouvrir un shell dans le conteneur Flask
	docker compose exec app bash

shell-db: ## [INFO] Ouvrir MySQL CLI
	docker compose exec db mysql -u flask_user -p

clean: ## [FAILED] Tout arrêter et supprimer les volumes
	@echo "$(YELLOW)[WARNING] Suppression des services et volumes...$(NC)"
	docker compose down -v

rebuild: ## [INFO] Reconstruire et redémarrer
	@echo "$(GREEN)[INFO] Reconstruction complète...$(NC)"
	docker compose down -v
	docker compose build --no-cache
	docker compose up -d

test-connection: ## [INFO] Tester la connexion à l'application
	@echo "$(GREEN)[INFO] Test de connexion...$(NC)"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost || echo "[FAILED] Connexion impossible"

backup: ## [OK] Sauvegarder la base de données
	@echo "$(GREEN)[OK] Création d'une sauvegarde...$(NC)"
	docker compose exec -T db mysqldump -u flask_user -pflask_password_456 gestion_users > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)[OK] Sauvegarde créée!$(NC)"

restore: ## [INFO] Restaurer la base depuis backup.sql
	@echo "$(YELLOW)[INFO] Restauration de la base...$(NC)"
	@if [ -f backup.sql ]; then \
		docker compose exec -T db mysql -u flask_user -pflask_password_456 gestion_users < backup.sql; \
		echo "$(GREEN)[OK] Restauration terminée!$(NC)"; \
	else \
		echo "$(YELLOW)[FAILED] Fichier backup.sql introuvable$(NC)"; \
	fi

install: build up ## [OK] Installation complète (build + up)
	@echo "$(GREEN)[OK] Installation terminée!$(NC)"
	@echo "$(YELLOW)[INFO] Attendez 10 secondes que MySQL s'initialise...$(NC)"
	@sleep 10
	@make status

dev: ## [INFO] Mode développement avec logs
	docker compose up

prune: ## [INFO] Nettoyer Docker (images, conteneurs, volumes non utilisés)
	@echo "$(YELLOW)[WARNING] Nettoyage de Docker...$(NC)"
	docker system prune -a --volumes