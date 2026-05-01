#!/bin/bash

# Local development setup for React + FastAPI app

set -e

echo "🔧 Setting up local development environment..."

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -r requirements-cpu.txt

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Setup environment
echo ""
echo "⚙️  Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "   Created .env file - please configure with your API keys"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the app locally:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    source venv/bin/activate"
echo "    uvicorn api.app:app --reload"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "  Then open: http://localhost:3000"
echo ""
