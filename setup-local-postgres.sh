#!/bin/bash
# Setup local PostgreSQL for development
# This creates a local database for fast stats (alternative to Neon)

set -e

echo "🐘 Setting up local PostgreSQL for Open Navigator..."
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed"
    echo ""
    echo "Install PostgreSQL:"
    echo "  • macOS: brew install postgresql"
    echo "  • Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "  • Windows: Download from https://www.postgresql.org/download/windows/"
    exit 1
fi

echo "✅ PostgreSQL is installed"

# Database name
DB_NAME="open_navigator_stats"
DB_USER="${POSTGRES_USER:-postgres}"

echo "📊 Creating database: $DB_NAME"
echo ""

# Try to create database (will fail if already exists, which is ok)
psql -U "$DB_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME"

echo "✅ Database ready: $DB_NAME"
echo ""

# Update .env if it doesn't have LOCAL_DATABASE_URL
if [ -f .env ]; then
    if ! grep -q "LOCAL_DATABASE_URL" .env; then
        echo "📝 Adding LOCAL_DATABASE_URL to .env"
        echo "" >> .env
        echo "# Local PostgreSQL for fast stats (development)" >> .env
        echo "LOCAL_DATABASE_URL=postgresql://$DB_USER:$DB_USER@localhost:5432/$DB_NAME" >> .env
    else
        echo "✅ LOCAL_DATABASE_URL already in .env"
    fi
else
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    # Update the LOCAL_DATABASE_URL line
    sed -i "s|LOCAL_DATABASE_URL=.*|LOCAL_DATABASE_URL=postgresql://$DB_USER:$DB_USER@localhost:5432/$DB_NAME|" .env
fi

echo ""
echo "🎯 Next steps:"
echo ""
echo "  1. Run migration to load data:"
echo "     python neon/migrate.py"
echo ""
echo "  2. Start the API server:"
echo "     ./start-all.sh"
echo ""
echo "  3. Test it works:"
echo "     curl http://localhost:8000/api/stats"
echo ""
echo "✨ You're using local PostgreSQL for development!"
echo "   (Production will automatically use Neon when deployed)"
