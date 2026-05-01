# Deployment Scripts

Scripts for setting up local development environments and deploying to production.

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

### deploy-databricks-app.sh
Deploys the application to Databricks Apps platform.

**Usage:**
```bash
./scripts/deployment/deploy-databricks-app.sh
```

**Requirements:**
- Databricks CLI configured
- Valid Databricks token in .env
