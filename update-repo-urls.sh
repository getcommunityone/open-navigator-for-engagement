#!/bin/bash

# Script to update repository URLs after renaming
# From: oral-health-policy-pulse
# To: open-navigator-for-engagement

echo "🔄 Updating repository URLs..."

OLD_REPO="oral-health-policy-pulse"
NEW_REPO="open-navigator-for-engagement"
GITHUB_ORG="getcommunityone"

# Find and replace in all relevant files
find . -type f \( \
    -name "*.md" -o \
    -name "*.py" -o \
    -name "*.ts" -o \
    -name "*.tsx" -o \
    -name "*.json" -o \
    -name "*.yaml" -o \
    -name "*.yml" \
\) -not -path "*/node_modules/*" \
   -not -path "*/.venv/*" \
   -not -path "*/.git/*" \
   -not -path "*/build/*" \
   -not -path "*/.docusaurus/*" \
   -exec sed -i "s|${GITHUB_ORG}/${OLD_REPO}|${GITHUB_ORG}/${NEW_REPO}|g" {} +

echo "✅ Updated repository URLs from ${OLD_REPO} to ${NEW_REPO}"
echo ""
echo "📝 Files updated:"
grep -r "open-navigator-for-engagement" . \
    --include="*.md" \
    --include="*.py" \
    --include="*.ts" \
    --exclude-dir=node_modules \
    --exclude-dir=.venv \
    --exclude-dir=.git \
    --exclude-dir=build \
    --exclude-dir=.docusaurus \
    | cut -d: -f1 | sort -u

echo ""
echo "🔍 Next steps:"
echo "1. Review changes: git diff"
echo "2. Commit changes: git add . && git commit -m 'Update repository name to open-navigator-for-engagement'"
echo "3. Push changes: git push"
