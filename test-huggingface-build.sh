#!/bin/bash
set -e

echo "🔨 Building Hugging Face Docker image..."
docker build -f Dockerfile.huggingface -t open-navigator-test .

echo ""
echo "✅ Build successful!"
echo ""
echo "🚀 Starting container on port 7860..."
docker run --rm -p 7860:7860 --name open-navigator-test open-navigator-test

# To run in background instead:
# docker run -d -p 7860:7860 --name open-navigator-test open-navigator-test
# 
# Then check logs with:
# docker logs -f open-navigator-test
#
# Stop with:
# docker stop open-navigator-test
