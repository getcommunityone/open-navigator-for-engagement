#!/bin/bash

echo "🚀 Starting Open Navigator for Engagement on Hugging Face Spaces"
echo "=================================================="
echo ""
echo "📊 Service Status:"
echo "  - Documentation: http://localhost:7860/docs"
echo "  - Main App: http://localhost:7860/"
echo "  - API: http://localhost:7860/api"
echo ""
echo "=================================================="
echo ""

# Start supervisor which manages nginx and FastAPI
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
