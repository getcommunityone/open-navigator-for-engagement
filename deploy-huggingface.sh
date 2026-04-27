#!/bin/bash

# Quick deployment script for Hugging Face Spaces
# Deploys all three apps: Documentation, Frontend, and API

set -e

# Parse command line arguments
SKIP_TEST=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-test)
            SKIP_TEST=true
            shift
            ;;
        *)
            HF_USERNAME_ARG="$1"
            shift
            ;;
    esac
done

echo "🚀 Open Navigator for Engagement - Hugging Face Deployment"
echo "==========================================================="
echo ""

# Check if HF username is provided (env var or argument)
if [ -z "$HF_USERNAME" ] && [ -z "$HF_USERNAME_ARG" ]; then
    echo "❌ Error: Hugging Face username required"
    echo ""
    echo "Usage Option 1 (Environment Variable):"
    echo "  export HF_USERNAME=your_username"
    echo "  ./deploy-huggingface.sh"
    echo ""
    echo "Usage Option 2 (Command Argument):"
    echo "  ./deploy-huggingface.sh YOUR_HF_USERNAME"
    echo ""
    echo "Usage Option 3 (Skip Docker test - not recommended):"
    echo "  ./deploy-huggingface.sh YOUR_HF_USERNAME --skip-test"
    echo ""
    echo "Example:"
    echo "  export HF_USERNAME=getcommunityone"
    echo "  ./deploy-huggingface.sh"
    echo ""
    exit 1
fi

# Use argument if provided, otherwise use env var
if [ -n "$HF_USERNAME_ARG" ]; then
    HF_USERNAME="$HF_USERNAME_ARG"
fi
SPACE_NAME="open-navigator-for-engagement"
HF_REPO="https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"

echo "📋 Deployment Configuration"
echo "  Username: $HF_USERNAME"
echo "  Space: $SPACE_NAME"
echo "  URL: $HF_REPO"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if huggingface-cli is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "📦 Installing huggingface-hub..."
    pip install huggingface-hub
fi

# Check if logged in
echo "🔐 Checking Hugging Face authentication..."
if ! huggingface-cli whoami &> /dev/null; then
    echo "❌ Not logged in to Hugging Face"
    echo "Please run: huggingface-cli login"
    exit 1
fi

echo "✅ Authenticated as: $(huggingface-cli whoami)"
echo ""

# Run Docker build test before deployment (unless skipped)
if [ "$SKIP_TEST" = true ]; then
    echo "⚠️  Skipping pre-deployment Docker build test (--skip-test flag)"
    echo ""
else
    echo "🧪 Running pre-deployment Docker build test..."
    echo "This ensures the build works before pushing to Hugging Face"
    echo ""

    if [ -f "./test-huggingface-build.sh" ]; then
        chmod +x ./test-huggingface-build.sh
        
        if ./test-huggingface-build.sh; then
            echo ""
            echo "✅ Pre-deployment test passed!"
            echo ""
        else
            echo ""
            echo "❌ Pre-deployment test failed!"
            echo ""
            echo "Please fix the Docker build issues before deploying."
            echo "Run './test-huggingface-build.sh' to test locally."
            echo ""
            echo "To deploy anyway (not recommended), use:"
            echo "  ./deploy-huggingface.sh $HF_USERNAME --skip-test"
            echo ""
            exit 1
        fi
    else
        echo "⚠️  Warning: test-huggingface-build.sh not found"
        echo "Skipping pre-deployment test"
        echo ""
    fi
fi

# Ask to create space if it doesn't exist
echo "🌟 Creating Hugging Face Space (if it doesn't exist)..."
huggingface-cli repo create "$SPACE_NAME" --type space --space-sdk docker --exist-ok || true
echo ""

# Create deployment branch
echo "🔧 Preparing deployment branch..."
git checkout -b huggingface-deploy 2>/dev/null || git checkout huggingface-deploy

# Copy Dockerfile for HF (they look for "Dockerfile" not "Dockerfile.huggingface")
echo "📝 Configuring Dockerfile..."
cp Dockerfile.huggingface Dockerfile

# Copy README for Space description
echo "📝 Configuring README..."
cp .huggingface/README.md README_HF.md

# Remove large binary files that will be included in Docker build
# (HF Spaces rejects large binary files in git)
echo "📝 Optimizing deployment (removing large binaries)..."
git rm --cached frontend/public/communityone_logo.png website/static/img/communityone_logo.png 2>/dev/null || true

# Stage deployment files
git add Dockerfile README_HF.md .huggingface/
git add -u

# Commit if there are changes
if git diff --cached --quiet; then
    echo "✅ No changes to commit"
else
    echo "💾 Committing deployment configuration..."
    git commit -m "Configure Hugging Face Space deployment" || true
fi

# Add HF remote if it doesn't exist
if git remote get-url hf &> /dev/null; then
    echo "✅ Hugging Face remote already configured"
else
    echo "🔗 Adding Hugging Face remote..."
    git remote add hf "$HF_REPO"
fi

# Push to Hugging Face
echo ""
echo "📤 Pushing to Hugging Face Spaces..."
echo "This will trigger a build (takes ~10-15 minutes)"
echo ""
git push hf huggingface-deploy:main --force

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "==========================================================="
echo "🎉 Next Steps:"
echo "==========================================================="
echo ""
echo "1. View your Space:"
echo "   https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"
echo ""
echo "2. Configure hardware (REQUIRED for Docker):"
echo "   - Go to Settings → Resource configuration"
echo "   - Select 'CPU Basic' (~\$22/month minimum)"
echo ""
echo "3. Add API keys as secrets:"
echo "   - Go to Settings → Variables and secrets"
echo "   - Add these secrets:"
echo "     • OPENAI_API_KEY"
echo "     • ANTHROPIC_API_KEY"
echo "     • HUGGINGFACE_TOKEN"
echo ""
echo "4. Monitor build progress:"
echo "   - Click 'Logs' tab in your Space"
echo "   - Build takes ~10-15 minutes"
echo ""
echo "5. Access your apps:"
echo "   - Main App: https://${HF_USERNAME}-${SPACE_NAME}.hf.space/"
echo "   - Documentation: https://${HF_USERNAME}-${SPACE_NAME}.hf.space/docs"
echo "   - API: https://${HF_USERNAME}-${SPACE_NAME}.hf.space/api/docs"
echo ""
echo "==========================================================="
echo ""
echo "📖 Full guide: ./HUGGINGFACE_DEPLOYMENT.md"
echo ""
