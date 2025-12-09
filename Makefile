
.PHONY: up down logs test test-backend shell-backend shell-db migrate makemigrations seed sim help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services in background
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## View logs for all services (follow)
	docker compose logs -f

logs-backend: ## View logs for backend only
	docker compose logs -f backend

logs-worker: ## View logs for celery worker
	docker compose logs -f celeryworker

test: ## Run backend tests
	docker compose exec backend pytest

shell-backend: ## Open bash shell in backend container
	docker compose exec backend bash

shell-db: ## Open PostgreSQL shell
	docker compose exec db psql -U postgres -d app

migrate: ## Apply database migrations
	docker compose exec backend alembic upgrade head

makemigrations: ## Create new migration (usage: make makemigrations msg="message")
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

seed: ## Trigger odds fetch task to seed mock data
	docker compose exec celeryworker celery -A app.worker call app.worker.run_odds_fetch

sim: ## Run a simulation manually (usage: make sim id=MATCH_UUID sims=2000)
	docker compose exec celeryworker python -c "from app.worker import run_tennis_simulation; import structlog; run_tennis_simulation('$(id)', n_sims=$(sims))"
