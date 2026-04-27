#!/bin/bash

# Setup script to install git hooks for build protection
# Run this once after cloning the repository

echo "🔧 Setting up git hooks for build protection..."
echo ""

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy pre-push hook
if [ -f ".githooks/pre-push" ]; then
    cp .githooks/pre-push .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    echo "✅ Installed pre-push hook"
else
    echo "❌ Error: .githooks/pre-push not found"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Git hooks installed successfully!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "What this does:"
echo "  • Before each 'git push', runs quick build checks"
echo "  • Catches TypeScript errors before they reach CI"
echo "  • Prevents broken builds from being pushed"
echo ""
echo "To bypass the hook (emergency only):"
echo "  git push --no-verify"
echo ""
