# ============================================================================
# Baby Foot ELO - Development Makefile
# ============================================================================
# Development commands for the Next.js full-stack application
# Usage: make <target>
# ============================================================================

.PHONY: help install dev build start format lint typecheck test test-watch test-local supabase-start supabase-stop supabase-status supabase-reset quality clean

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
	@echo "  install              Install all dependencies (bun)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  dev                  Start development server (Next.js, port 3000)"
	@echo "  build                Build for production"
	@echo "  start                Start production server"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  format               Format code (prettier)"
	@echo "  lint                 Lint code (ESLint)"
	@echo "  typecheck            Run TypeScript type check"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  test                 Run tests once (vitest)"
	@echo "  test-watch           Run tests in watch mode"
	@echo "  test-local           Run tests with local Supabase (all-in-one)"
	@echo ""
	@echo "$(GREEN)Supabase Local:$(NC)"
	@echo "  supabase-start       Start local Supabase instance"
	@echo "  supabase-stop        Stop local Supabase instance"
	@echo "  supabase-status      Check local Supabase status"
	@echo "  supabase-reset       Reset local database"
	@echo ""
	@echo "$(GREEN)Quality Gate:$(NC)"
	@echo "  quality              Run lint, typecheck, and tests (pre-commit)"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  clean                Remove node_modules and build artifacts"
	@echo ""

# ============================================================================
# Installation
# ============================================================================

install:
	@echo "$(CYAN)Installing dependencies...$(NC)"
	bun install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

# ============================================================================
# Development
# ============================================================================

dev:
	@echo "$(CYAN)Starting development server...$(NC)"
	@echo "$(YELLOW)http://localhost:3000$(NC)"
	@echo ""
	bun run dev

build:
	@echo "$(CYAN)Building for production...$(NC)"
	bun run build
	@echo "$(GREEN)✓ Build completed$(NC)"

start:
	@echo "$(CYAN)Starting production server...$(NC)"
	bun run start

# ============================================================================
# Code Quality
# ============================================================================

format:
	@echo "$(CYAN)Formatting code...$(NC)"
	bun run format
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint:
	@echo "$(CYAN)Linting code...$(NC)"
	bun run lint
	@echo "$(GREEN)✓ Linting passed$(NC)"

typecheck:
	@echo "$(CYAN)Type checking...$(NC)"
	bun run typecheck
	@echo "$(GREEN)✓ Type check passed$(NC)"

# ============================================================================
# Testing
# ============================================================================

test:
	@echo "$(CYAN)Running tests...$(NC)"
	bun run test:run
	@echo "$(GREEN)✓ Tests passed$(NC)"

test-watch:
	@echo "$(CYAN)Running tests in watch mode...$(NC)"
	bun run test

test-local:
	@echo "$(CYAN)Running tests with local Supabase...$(NC)"
	bun run test:local
	@echo "$(GREEN)✓ Tests passed$(NC)"

# ============================================================================
# Supabase Local Development
# ============================================================================

supabase-start:
	@echo "$(CYAN)Starting local Supabase...$(NC)"
	bun run supabase:start
	@echo "$(GREEN)✓ Supabase started$(NC)"

supabase-stop:
	@echo "$(CYAN)Stopping local Supabase...$(NC)"
	bun run supabase:stop
	@echo "$(GREEN)✓ Supabase stopped$(NC)"

supabase-status:
	@echo "$(CYAN)Checking Supabase status...$(NC)"
	bun run supabase:status

supabase-reset:
	@echo "$(YELLOW)Resetting local Supabase database...$(NC)"
	bun run supabase:reset
	@echo "$(GREEN)✓ Database reset$(NC)"

# ============================================================================
# Quality Gate (pre-commit)
# ============================================================================

quality: lint typecheck test-local
	@echo ""
	@echo "$(GREEN)============================================$(NC)"
	@echo "$(GREEN)✓ All quality checks passed!$(NC)"
	@echo "$(GREEN)============================================$(NC)"

# ============================================================================
# Cleanup
# ============================================================================

clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	rm -rf node_modules
	rm -rf .next
	@echo "$(GREEN)✓ Cleanup completed$(NC)"
