.PHONY: help install install-frontend install-docs build-frontend build-docs clean test run dev dev-frontend dev-docs start-all stop-all dev-full docker-up docker-down deploy-databricks

help:
	@echo "🦷 Open Navigator - Makefile Commands"
	@echo "===================================================="
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make start-all         - Start ALL services (API + Dashboard + Docs) with tmux"
	@echo "  make stop-all          - Stop all running services"
	@echo ""
	@echo "🐍 Python Backend:"
	@echo "  make install           - Install Python dependencies in venv"
	@echo "  make dev               - Start backend with auto-reload"
	@echo "  make run               - Start backend (production)"
	@echo ""
	@echo "⚛️  React Dashboard:"
	@echo "  make install-frontend  - Install dashboard npm dependencies"
	@echo "  make build-frontend    - Build React dashboard for production"
	@echo "  make dev-frontend      - Start dashboard dev server"
	@echo ""
	@echo "📚 Documentation Site:"
	@echo "  make install-docs      - Install Docusaurus dependencies"
	@echo "  make build-docs        - Build documentation for production"
	@echo "  make dev-docs          - Start documentation dev server"
	@echo ""
	@echo "☁️  Deployment:"
	@echo "  make deploy-databricks - Deploy to Databricks Apps"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-up         - Start Docker containers"
	@echo "  make docker-down       - Stop Docker containers"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test              - Run test suite"
	@echo "  make clean             - Remove build artifacts"
	@echo ""

install:
	@echo "📦 Creating virtual environment and installing dependencies..."
	@chmod +x install.sh
	@./install.sh

install-frontend:
	@echo "📦 Installing dashboard dependencies..."
	@cd frontend && npm install
	@echo "✅ Dashboard dependencies installed!"

install-docs:
	@echo "📦 Installing documentation dependencies..."
	@cd website && npm install
	@echo "✅ Documentation dependencies installed!"

build-frontend:
	@echo "🔨 Building React dashboard..."
	@cd frontend && npm run build
	@echo "✅ Dashboard built to api/static/"

build-docs:
	@echo "🔨 Building documentation site..."
	@cd website && npm run build
	@echo "✅ Documentation built to website/build/"

clean:
	@echo "🧹 Cleaning up..."
	@rm -rf .venv venv
	@rm -rf frontend/node_modules frontend/dist
	@rm -rf website/node_modules website/build website/.docusaurus
	@rm -rf api/static
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
	@rm -rf logs/*.pid logs/*.log
	@echo "✅ Cleanup complete"

test:
	@echo "🧪 Running tests..."
	@. venv/bin/activate && pytest tests/ -v

run: build-frontend
	@echo "🚀 Starting application (production mode)..."
	@. venv/bin/activate && uvicorn api.app:app --host 0.0.0.0 --port 8000

dev:
	@echo "🔧 Starting backend with auto-reload..."
	@echo "📡 Backend running at http://localhost:8000"
	@. venv/bin/activate && uvicorn api.app:app --reload

dev-frontend:
	@echo "⚛️  Starting dashboard dev server..."
	@echo "📡 Dashboard running at http://localhost:5173"
	@cd frontend && npm run dev

dev-docs:
	@echo "📚 Starting documentation dev server..."
	@echo "📡 Documentation running at http://localhost:3000"
	@cd website && npm start

start-all:
	@echo "🚀 Starting all services with tmux..."
	@chmod +x start-all.sh
	@./start-all.sh

stop-all:
	@echo "🛑 Stopping all services..."
	@chmod +x stop-all.sh
	@./stop-all.sh

dev-full:
	@echo "🚀 Use 'make start-all' for better experience with tmux!"
	@echo ""
	@echo "Starting backend and frontend (manual)..."
	@echo "📡 Backend:   http://localhost:8000"
	@echo "📡 Dashboard: http://localhost:5173"
	@echo "📡 Docs:      http://localhost:3000 (run 'make dev-docs' in another terminal)"
	@echo ""
	@. venv/bin/activate && uvicorn api.app:app --reload & \
	cd frontend && npm run dev

deploy-databricks:
	@echo "☁️  Deploying to Databricks Apps..."
	@chmod +x scripts/deploy-databricks-app.sh
	@./scripts/deploy-databricks-app.sh

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
