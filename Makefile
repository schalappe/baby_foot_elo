# ============================================================================
# Baby Foot ELO - Development Makefile
# ============================================================================
# Unified development commands for the monorepo (backend + frontend)
# Usage: make <target>
# ============================================================================

.PHONY: help install install-backend install-frontend \
        dev dev-backend dev-frontend \
        format format-backend format-frontend \
        lint lint-backend lint-frontend \
        typecheck typecheck-frontend \
        test test-backend test-backend-v test-backend-cov test-frontend test-frontend-watch \
        build quality clean clean-cache

# ============================================================================
# Configuration
# ============================================================================

BACKEND_DIR := backend
FRONTEND_DIR := frontend

# Colors for terminal output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m

# ============================================================================
# Help
# ============================================================================

help:
	@echo ""
	@echo "$(CYAN)Baby Foot ELO - Development Commands$(NC)"
	@echo "======================================"
	@echo ""
	@echo "$(GREEN)Installation:$(NC)"
	@echo "  install              Install all dependencies (backend + frontend)"
	@echo "  install-backend      Install backend dependencies (Poetry)"
	@echo "  install-frontend     Install frontend dependencies (bun)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  dev                  Start both backend and frontend servers"
	@echo "  dev-backend          Start backend server (uvicorn, port 8000)"
	@echo "  dev-frontend         Start frontend server (Next.js, port 3000)"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  format               Format all code"
	@echo "  format-backend       Format Python code (black + isort)"
	@echo "  format-frontend      Format frontend code (prettier)"
	@echo "  lint                 Lint all code"
	@echo "  lint-backend         Lint Python code (pylint)"
	@echo "  lint-frontend        Lint frontend code (ESLint)"
	@echo "  typecheck            Run type checks"
	@echo "  typecheck-frontend   Run TypeScript type check"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  test                 Run all tests (backend + frontend)"
	@echo "  test-backend         Run backend tests (pytest)"
	@echo "  test-backend-v       Run backend tests with verbose output"
	@echo "  test-backend-cov     Run backend tests with coverage"
	@echo "  test-frontend        Run frontend tests (vitest)"
	@echo "  test-frontend-watch  Run frontend tests in watch mode"
	@echo ""
	@echo "$(GREEN)Build:$(NC)"
	@echo "  build                Build frontend for production"
	@echo "  quality              Run lint, typecheck, and tests (pre-commit)"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  clean                Remove virtual envs and node_modules"
	@echo "  clean-cache          Remove Python cache files"
	@echo ""

# ============================================================================
# Installation
# ============================================================================

install: install-backend install-frontend
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

install-backend:
	@echo "$(CYAN)Installing backend dependencies...$(NC)"
	cd $(BACKEND_DIR) && poetry install
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

install-frontend:
	@echo "$(CYAN)Installing frontend dependencies...$(NC)"
	cd $(FRONTEND_DIR) && bun install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

# ============================================================================
# Development Servers
# ============================================================================

dev:
	@echo "$(CYAN)Starting development servers...$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8000$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo ""
	bun run dev

dev-backend:
	@echo "$(CYAN)Starting backend server...$(NC)"
	cd $(BACKEND_DIR) && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "$(CYAN)Starting frontend server...$(NC)"
	cd $(FRONTEND_DIR) && bun run dev

# ============================================================================
# Formatting
# ============================================================================

format: format-backend format-frontend
	@echo "$(GREEN)✓ All code formatted$(NC)"

format-backend:
	@echo "$(CYAN)Formatting backend code...$(NC)"
	cd $(BACKEND_DIR) && poetry run black .
	cd $(BACKEND_DIR) && poetry run isort .
	@echo "$(GREEN)✓ Backend code formatted$(NC)"

format-frontend:
	@echo "$(CYAN)Formatting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && bun run format
	@echo "$(GREEN)✓ Frontend code formatted$(NC)"

# ============================================================================
# Linting
# ============================================================================

lint: lint-backend lint-frontend
	@echo "$(GREEN)✓ All linting passed$(NC)"

lint-backend:
	@echo "$(CYAN)Linting backend code...$(NC)"
	cd $(BACKEND_DIR) && poetry run pylint app/
	@echo "$(GREEN)✓ Backend linting passed$(NC)"

lint-frontend:
	@echo "$(CYAN)Linting frontend code...$(NC)"
	cd $(FRONTEND_DIR) && bun run lint
	@echo "$(GREEN)✓ Frontend linting passed$(NC)"

# ============================================================================
# Type Checking
# ============================================================================

typecheck: typecheck-frontend
	@echo "$(GREEN)✓ All type checks passed$(NC)"

typecheck-frontend:
	@echo "$(CYAN)Type checking frontend...$(NC)"
	cd $(FRONTEND_DIR) && bun run typecheck
	@echo "$(GREEN)✓ Frontend type check passed$(NC)"

# ============================================================================
# Testing
# ============================================================================

test: test-backend test-frontend
	@echo "$(GREEN)✓ All tests passed$(NC)"

test-backend:
	@echo "$(CYAN)Running backend tests...$(NC)"
	cd $(BACKEND_DIR) && poetry run pytest tests/
	@echo "$(GREEN)✓ Backend tests passed$(NC)"

test-backend-v:
	@echo "$(CYAN)Running backend tests (verbose)...$(NC)"
	cd $(BACKEND_DIR) && poetry run pytest tests/ -v
	@echo "$(GREEN)✓ Backend tests passed$(NC)"

test-backend-cov:
	@echo "$(CYAN)Running backend tests with coverage...$(NC)"
	cd $(BACKEND_DIR) && poetry run pytest tests/ --cov=app --cov-report=term-missing
	@echo "$(GREEN)✓ Backend tests with coverage completed$(NC)"

test-frontend:
	@echo "$(CYAN)Running frontend tests...$(NC)"
	cd $(FRONTEND_DIR) && bun run test:run
	@echo "$(GREEN)✓ Frontend tests passed$(NC)"

test-frontend-watch:
	@echo "$(CYAN)Running frontend tests in watch mode...$(NC)"
	cd $(FRONTEND_DIR) && bun run test

# ============================================================================
# Build
# ============================================================================

build:
	@echo "$(CYAN)Building frontend for production...$(NC)"
	cd $(FRONTEND_DIR) && bun run build
	@echo "$(GREEN)✓ Frontend build completed$(NC)"

# ============================================================================
# Quality Gate (pre-commit)
# ============================================================================

quality: lint typecheck test
	@echo ""
	@echo "$(GREEN)============================================$(NC)"
	@echo "$(GREEN)✓ All quality checks passed!$(NC)"
	@echo "$(GREEN)============================================$(NC)"

# ============================================================================
# Cleanup
# ============================================================================

clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	rm -rf $(BACKEND_DIR)/.venv
	rm -rf $(FRONTEND_DIR)/node_modules
	rm -rf $(FRONTEND_DIR)/.next
	rm -rf node_modules
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

clean-cache:
	@echo "$(YELLOW)Removing Python cache files...$(NC)"
	find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find $(BACKEND_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	find $(BACKEND_DIR) -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cache cleanup completed$(NC)"
