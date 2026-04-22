.PHONY: help install install-frontend build-frontend clean test run dev dev-frontend dev-full docker-up docker-down deploy-databricks

help:
	@echo "Oral Health Policy Pulse - Makefile Commands"
	@echo "============================================="
	@echo ""
	@echo "🐍 Python Backend:"
	@echo "  make install           - Install Python dependencies in venv"
	@echo "  make dev               - Start backend with auto-reload"
	@echo "  make run               - Start backend (production)"
	@echo ""
	@echo "⚛️  React Frontend:"
	@echo "  make install-frontend  - Install npm dependencies"
	@echo "  make build-frontend    - Build React app for production"
	@echo "  make dev-frontend      - Start frontend dev server"
	@echo ""
	@echo "🚀 Full Stack:"
	@echo "  make dev-full          - Run both backend and frontend"
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
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "✅ Frontend dependencies installed!"

build-frontend:
	@echo "🔨 Building React frontend..."
	@cd frontend && npm run build
	@echo "✅ Frontend built to api/static/"

clean:
	@echo "🧹 Cleaning up..."
	@rm -rf venv
	@rm -rf frontend/node_modules
	@rm -rf frontend/dist
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
	@echo "⚛️  Starting frontend dev server..."
	@echo "📡 Frontend running at http://localhost:3000"
	@cd frontend && npm run dev

dev-full:
	@echo "🚀 Starting full-stack development environment..."
	@echo "📡 Backend:  http://localhost:8000"
	@echo "📡 Frontend: http://localhost:3000"
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
