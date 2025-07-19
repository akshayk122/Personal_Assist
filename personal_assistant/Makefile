# Personal Assistant Makefile
# Provides common development tasks using uv

.PHONY: help install install-dev test lint format clean servers meeting expense orchestrator streamlit demo test-supabase

# Default target
help:
	@echo "Personal Assistant Development Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  test         - Run test suite"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean cache and build files"
	@echo ""
	@echo "Server Commands:"
	@echo "  servers      - Start all servers (requires 3 terminals)"
	@echo "  meeting      - Start meeting server (port 8100)"
	@echo "  expense      - Start expense server (port 8200)"
	@echo "  orchestrator - Start orchestrator server (port 8300)"
	@echo "  streamlit    - Start Streamlit UI (port 8501)"
	@echo "  demo         - Run demo script to test the system"
	@echo "  test-supabase - Test Supabase connection and integration"
	@echo ""
	@echo "Usage: make <command>"

# Installation
install:
	@echo "📦 Installing production dependencies..."
	uv sync

install-dev:
	@echo "📦 Installing development dependencies..."
	uv sync --extra dev

# Testing
test:
	@echo "🧪 Running test suite..."
	uv run pytest tests/ -v

test-coverage:
	@echo "🧪 Running test suite with coverage..."
	uv run pytest --cov=personal_assistant --cov-report=term-missing --cov-report=html

test-fast:
	@echo "🧪 Running fast tests only..."
	uv run pytest -m "not slow" -v

# Code Quality
lint:
	@echo "🔍 Running code linting..."
	uv run flake8 personal_assistant tests
	uv run mypy personal_assistant

format:
	@echo "✨ Formatting code..."
	uv run black personal_assistant tests
	uv run isort personal_assistant tests

format-check:
	@echo "🔍 Checking code formatting..."
	uv run black --check personal_assistant tests
	uv run isort --check-only personal_assistant tests

# Development Environment
clean:
	@echo "🧹 Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Server Management
servers:
	@echo "🚀 Starting all servers..."
	@echo "⚠️  This requires 3 separate terminals:"
	@echo "   Terminal 1: make meeting"
	@echo "   Terminal 2: make expense" 
	@echo "   Terminal 3: make orchestrator"

meeting:
	@echo "🕐 Starting Meeting Manager Server (port 8100)..."
	uv run python servers/meeting_server.py

expense:
	@echo "💰 Starting Expense Tracker Server (port 8200)..."
	uv run python servers/expense_server.py

orchestrator:
	@echo "🤖 Starting Orchestrator Server (port 8300)..."
	uv run python servers/orchestrator_server.py

streamlit:
	@echo "💻 Starting Streamlit UI (port 8501)..."
	uv run python run_streamlit.py

demo:
	@echo "🧪 Running Personal Assistant Demo..."
	uv run python demo.py

test-supabase:
	@echo "🔗 Testing Supabase Connection..."
	uv run python test_supabase.py

# Alternative server commands using project scripts
meeting-script:
	@echo "🕐 Starting Meeting Manager via script..."
	uv run meeting-server

expense-script:
	@echo "💰 Starting Expense Tracker via script..."
	uv run expense-server

orchestrator-script:
	@echo "🤖 Starting Orchestrator via script..."
	uv run orchestrator-server

# Development workflow
dev-setup: install-dev
	@echo "🛠️  Development environment setup complete!"
	@echo "📝 Next steps:"
	@echo "   1. Copy env.example to .env and add your GOOGLE_API_KEY"
	@echo "   2. Run 'make servers' to start all servers"
	@echo "   3. Run 'make test' to verify everything works"

# Quick development check
check: format-check lint test-fast
	@echo "✅ Development checks passed!"

# Full development check
check-full: format-check lint test
	@echo "✅ Full development checks passed!"

# Build and package
build:
	@echo "📦 Building package..."
	uv build

# Documentation
docs:
	@echo "📚 Building documentation..."
	uv sync --extra docs
	uv run mkdocs build

docs-serve:
	@echo "📚 Serving documentation locally..."
	uv sync --extra docs
	uv run mkdocs serve 