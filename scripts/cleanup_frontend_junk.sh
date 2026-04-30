#!/bin/bash
# Clean up garbage files created by terminal corruption
cd /home/developer/projects/oral-health-policy-pulse/frontend

echo "Removing garbage files..."
find . -maxdepth 1 -type f -name "*fluorid*" -delete
find . -maxdepth 1 -type f -name "*lativesession*" -delete  
find . -maxdepth 1 -type f -name "*misclassification*" -delete
find . -maxdepth 1 -type f -name "*tgres*" -delete
find . -maxdepth 1 -type f -name "*readlines*" -delete
find . -maxdepth 1 -type f -name "= *" -delete
find . -maxdepth 1 -type f -name "s more" -delete
find . -maxdepth 1 -type f -name "0" ! -name "*.ts" ! -name "*.js" -delete 2>/dev/null

# Clean up any other non-standard files (not .ts, .js, .json, .md, .html, dot files)
for file in *; do
    if [[ -f "$file" && ! "$file" =~ \.(ts|js|json|md|html|cjs|txt)$ && ! "$file" =~ ^\. ]]; then
        case "$file" in
            package.json|package-lock.json|tsconfig.json|tsconfig.node.json|vite.config.ts|tailwind.config.js|postcss.config.js|index.html|README.md)
                # Keep these
                ;;
            *)
                echo "  Removing: $file"
                rm -f "$file"
                ;;
        esac
    fi
done

echo "✅ Cleanup complete"
ls -1 | grep -v node_modules | head -20
