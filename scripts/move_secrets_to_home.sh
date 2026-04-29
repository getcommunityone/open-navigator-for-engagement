#!/bin/bash
# Move all secret files from project to home directory for better security

set -e

PROJECT_SECRETS="$HOME/projects/oral-health-policy-pulse/secrets"
HOME_GCP="$HOME/.gcp"

echo "🔐 Moving secrets from project to home directory..."

# Create home .gcp directory if it doesn't exist
mkdir -p "$HOME_GCP"

# Check if secrets directory exists
if [ ! -d "$PROJECT_SECRETS" ]; then
    echo "❌ Secrets directory not found: $PROJECT_SECRETS"
    exit 1
fi

# Count files
file_count=$(find "$PROJECT_SECRETS" -maxdepth 1 -type f | wc -l)

if [ "$file_count" -eq 0 ]; then
    echo "✅ No files to move in $PROJECT_SECRETS"
    exit 0
fi

echo "📁 Found $file_count file(s) to move"

# Move all files
for file in "$PROJECT_SECRETS"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "   Moving: $filename"
        mv "$file" "$HOME_GCP/$filename"
        chmod 600 "$HOME_GCP/$filename"
        echo "   ✅ Moved to: $HOME_GCP/$filename (permissions: 600)"
    fi
done

# List moved files
echo ""
echo "✅ All secrets moved successfully!"
echo ""
echo "📂 Files now in $HOME_GCP:"
ls -lh "$HOME_GCP"

echo ""
echo "🔧 Next steps:"
echo "1. Update your .env file with:"
echo "   GOOGLE_APPLICATION_CREDENTIALS=$HOME_GCP/bigquery-credentials.json"
echo ""
echo "2. Or if you have multiple files, use the specific one you need"
