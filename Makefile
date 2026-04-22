.PHONY: help install clean test run dev docker-up docker-down

help:
	@echo "Oral Health Policy Pulse - Makefile Commands"
	@echo "============================================="
	@echo ""
	@echo "  make install      - Install dependencies in virtual environment"
	@echo "  make clean        - Remove virtual environment and cache files"
	@echo "  make test         - Run test suite"
	@echo "  make run          - Start the API server"
	@echo "  make dev          - Start API server in development mode"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make example      - Run example workflow"
	@echo "  make heatmap      - Generate example heatmap"
	@echo ""

install:
	@echo "Creating virtual environment and installing dependencies..."
	@chmod +x install.sh
	@./install.sh

clean:
	@echo "Cleaning up..."
	@rm -rf venv
	@rm -rf __pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@echo "✓ Cleanup complete"

test:
	@echo "Running tests..."
	@. venv/bin/activate && pytest tests/ -v

run:
	@echo "Starting API server..."
	@. venv/bin/activate && python main.py serve

dev:
	@echo "Starting API server in development mode..."
	@. venv/bin/activate && python main.py serve --reload

docker-up:
	@echo "Starting Docker containers..."
	@docker-compose up -d
	@echo "✓ Containers started"
	@echo "  API: http://localhost:8000"
	@echo "  Docs: http://localhost:8000/docs"

docker-down:
	@echo "Stopping Docker containers..."
	@docker-compose down
	@echo "✓ Containers stopped"

example:
	@echo "Running example workflow..."
	@. venv/bin/activate && python examples/example_workflow.py

heatmap:
	@echo "Generating example heatmap..."
	@. venv/bin/activate && python main.py generate-heatmap --output example_heatmap.html
	@echo "✓ Heatmap saved to example_heatmap.html"

init:
	@echo "Initializing system..."
	@. venv/bin/activate && python main.py init

status:
	@echo "Checking system status..."
	@. venv/bin/activate && python main.py status

format:
	@echo "Formatting code..."
	@. venv/bin/activate && black .
	@. venv/bin/activate && ruff check . --fix
	@echo "✓ Code formatted"

lint:
	@echo "Linting code..."
	@. venv/bin/activate && ruff check .
	@. venv/bin/activate && mypy agents/ pipeline/ visualization/ api/
