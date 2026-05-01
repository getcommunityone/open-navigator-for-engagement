# Maintenance Scripts

System maintenance, cleanup, and development utilities.

## Cleanup Scripts

### cleanup_disk_space.sh
Frees up disk space by removing temporary files and caches.

**Usage:**
```bash
./scripts/maintenance/cleanup_disk_space.sh
```

**What it removes:**
- Docker images and containers
- Python cache files
- Node.js cache
- Temporary build artifacts

**⚠️ Does NOT remove:**
- Application data cache (`data/cache/`)
- Database files
- Important project data

### cleanup_frontend_junk.sh
Removes frontend build artifacts and dependencies.

**Usage:**
```bash
./scripts/maintenance/cleanup_frontend_junk.sh
```

### docker-cleanup.sh
Docker-specific cleanup (removes unused images, containers, volumes).

**Usage:**
```bash
./scripts/maintenance/docker-cleanup.sh
```

**What it cleans:**
- Stopped containers
- Unused images
- Dangling volumes
- Unused networks

## Project Maintenance

### migrate-docs.sh
Migrates documentation from project root to website/docs/ (Docusaurus format).

**Usage:**
```bash
./scripts/maintenance/migrate-docs.sh
```

**What it does:**
- Moves .md files from root to website/docs/
- Adds YAML frontmatter
- Converts filenames to kebab-case

## System Utilities

### prevent_terminal_corruption.sh
Prevents terminal corruption from Unicode characters.

**Usage:**
```bash
source scripts/maintenance/prevent_terminal_corruption.sh
```

### move_secrets_to_home.sh
Moves secrets to home directory for security.

**Usage:**
```bash
./scripts/maintenance/move_secrets_to_home.sh
```

## Development

### test-app.py
Quick test script for application functionality.

**Usage:**
```bash
python scripts/maintenance/test-app.py
```
