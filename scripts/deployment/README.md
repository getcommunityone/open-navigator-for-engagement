# Deployment Scripts

Scripts for setting up local development environments and deploying to production.

## Initial Setup

### install.sh
**Main installation script** - installs all dependencies and sets up the project.

**Usage:**
```bash
./scripts/deployment/install.sh
```

**What it does:**
- Installs Python dependencies
- Sets up virtual environment
- Configures environment variables
- Initializes databases

### setup-git-hooks.sh
Sets up pre-commit/pre-push hooks for code quality checks.

**Usage:**
```bash
./scripts/deployment/setup-git-hooks.sh
```

**Hooks installed:**
- TypeScript compilation check
- Python syntax check
- Frontend build test

## Scripts

### setup-local.sh
Sets up local development environment with required dependencies.

**Usage:**
```bash
./scripts/deployment/setup-local.sh
```

### setup_openstates_db.sh
Initializes and populates OpenStates PostgreSQL database with legislative data.

**Usage:**
```bash
./scripts/deployment/setup_openstates_db.sh
```

**What it does:**
- Downloads OpenStates PostgreSQL dumps
- Restores schema and data
- Sets up PostGIS extensions

### setup-local-postgres.sh
Alternative PostgreSQL setup for local development (without Docker).

**Usage:**
```bash
./scripts/deployment/setup-local-postgres.sh
```

**What it does:**
- Installs PostgreSQL 18 natively
- Configures local databases
- Sets up PostGIS extension

## Production Deployment

### deploy-databricks-app.sh
Deploys the application to Databricks Apps platform.

**Usage:**
```bash
./scripts/deployment/deploy-databricks-app.sh
```

**Requirements:**
- Databricks CLI configured
- Valid Databricks token in .env
