# Makefile for Codebase Audiobook local development
# Usage: make dev (starts everything)

.PHONY: help dev dev-services dev-backend dev-frontend stop clean install test

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Codebase Audiobook - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Main Commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install all dependencies (frontend + backend)
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	npm install --legacy-peer-deps
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && python3 -m venv ../.venv || true
	. .venv/bin/activate && pip install -U pip setuptools wheel
	. .venv/bin/activate && pip install -r backend/requirements.txt
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

dev-services: ## Start PostgreSQL and Redis in Docker
	@echo "$(BLUE)Starting PostgreSQL and Redis...$(NC)"
	docker compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "  - PostgreSQL: localhost:5433"
	@echo "  - Redis: localhost:6380"

dev-backend: dev-services ## Start backend server (with auto-reload)
	@echo "$(BLUE)Starting backend server...$(NC)"
	@echo "$(YELLOW)Waiting for PostgreSQL to be ready...$(NC)"
	@bash -c 'until docker compose -f docker-compose.dev.yml exec -T postgres pg_isready -U audiobook > /dev/null 2>&1; do sleep 1; done'
	@echo "$(GREEN)✓ PostgreSQL ready$(NC)"
	cd backend && . ../.venv/bin/activate && PYTHONPATH=$(PWD) python3 main.py

dev-frontend: ## Start frontend dev server (with hot reload)
	@echo "$(BLUE)Starting frontend dev server...$(NC)"
	npm run dev

dev: ## Start full development environment (services + backend + frontend)
	@echo "$(BLUE)Starting full development environment...$(NC)"
	@$(MAKE) dev-services
	@echo ""
	@echo "$(GREEN)Services are running. Now start backend and frontend in separate terminals:$(NC)"
	@echo "  Terminal 1: $(YELLOW)make dev-backend$(NC)"
	@echo "  Terminal 2: $(YELLOW)make dev-frontend$(NC)"
	@echo ""
	@echo "Or run them in background:"
	@echo "  $(YELLOW)make dev-backend &$(NC)"
	@echo "  $(YELLOW)make dev-frontend &$(NC)"

stop: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker compose -f docker-compose.dev.yml down
	@echo "$(GREEN)✓ Services stopped$(NC)"

clean: ## Stop services and remove volumes (WARNING: deletes database!)
	@echo "$(RED)WARNING: This will delete all database data!$(NC)"
	@read -p "Are you sure? (y/N): " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose -f docker-compose.dev.yml down -v; \
		echo "$(GREEN)✓ Services stopped and data cleaned$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

logs: ## Show logs from services
	docker compose -f docker-compose.dev.yml logs -f

logs-postgres: ## Show PostgreSQL logs
	docker compose -f docker-compose.dev.yml logs -f postgres

logs-redis: ## Show Redis logs
	docker compose -f docker-compose.dev.yml logs -f redis

test: ## Run backend tests
	cd backend && . ../.venv/bin/activate && PYTHONPATH=$(PWD) pytest

test-coverage: ## Run tests with coverage
	cd backend && . ../.venv/bin/activate && PYTHONPATH=$(PWD) pytest --cov=backend --cov-report=html

db-shell: ## Open PostgreSQL shell
	docker compose -f docker-compose.dev.yml exec postgres psql -U audiobook -d audiobook

redis-shell: ## Open Redis CLI
	docker compose -f docker-compose.dev.yml exec redis redis-cli

status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@docker compose -f docker-compose.dev.yml ps
