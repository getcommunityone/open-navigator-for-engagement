#!/bin/bash

# Docker Cleanup Script
# Removes unused Docker images, containers, volumes, and build cache
# Run this periodically to prevent disk space issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Docker Cleanup Utility${NC}"
echo "==========================================="
echo ""

# Show current disk usage
echo -e "${BLUE}📊 Current Docker disk usage:${NC}"
docker system df
echo ""

# Parse arguments
AGGRESSIVE=false
if [[ "$1" == "--aggressive" || "$1" == "-a" ]]; then
    AGGRESSIVE=true
fi

if [ "$AGGRESSIVE" = true ]; then
    echo -e "${YELLOW}⚠️  Running AGGRESSIVE cleanup (removes ALL unused data)${NC}"
    echo ""
    echo "This will remove:"
    echo "  - All stopped containers"
    echo "  - All networks not used by at least one container"
    echo "  - All dangling images"
    echo "  - All unused images (not just dangling)"
    echo "  - All build cache"
    echo "  - All volumes not used by at least one container"
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 1
    fi
    echo ""
    
    echo -e "${BLUE}🗑️  Removing all unused Docker data...${NC}"
    docker system prune -a -f --volumes
    
else
    echo -e "${BLUE}🗑️  Running standard cleanup...${NC}"
    echo ""
    echo "This will remove:"
    echo "  - All stopped containers"
    echo "  - All networks not used by at least one container"
    echo "  - All dangling images"
    echo "  - Build cache older than 24 hours"
    echo ""
    
    # Remove stopped containers
    echo -e "${YELLOW}Removing stopped containers...${NC}"
    docker container prune -f
    
    # Remove dangling images
    echo -e "${YELLOW}Removing dangling images...${NC}"
    docker image prune -f
    
    # Remove unused networks
    echo -e "${YELLOW}Removing unused networks...${NC}"
    docker network prune -f
    
    # Remove build cache older than 24 hours
    echo -e "${YELLOW}Removing old build cache...${NC}"
    docker builder prune -f --filter "until=24h"
fi

echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""

# Show updated disk usage
echo -e "${BLUE}📊 Updated Docker disk usage:${NC}"
docker system df
echo ""

echo "==========================================="
echo -e "${GREEN}💡 Tips:${NC}"
echo ""
echo "Run this script regularly to prevent disk space issues:"
echo ""
echo "  Standard cleanup (safe):"
echo "    ./docker-cleanup.sh"
echo ""
echo "  Aggressive cleanup (removes ALL unused data):"
echo "    ./docker-cleanup.sh --aggressive"
echo ""
echo "Add to crontab for weekly cleanup:"
echo "    0 2 * * 0 /path/to/docker-cleanup.sh > /dev/null 2>&1"
echo ""
echo "==========================================="
