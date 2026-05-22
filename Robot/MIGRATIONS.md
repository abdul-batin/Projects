# Database Migrations Guide

## Overview

The Robot Wall Planner uses a **decoupled migration system** where database schema initialization is separated from application runtime. This ensures:

- ✅ Clean separation of concerns
- ✅ Explicit database state management
- ✅ No schema modifications during normal operations
- ✅ Predictable startup behavior

---

## Migration Philosophy

### Before (Tightly Coupled)
```
Application Startup
    ↓
Check if tables exist
    ↓
Create tables if missing ← Mixed responsibility
    ↓
Start serving requests
```

**Problems:**
- Application responsible for schema management
- Unpredictable startup behavior
- Schema changes coupled with deployment
- Difficult to track migration history

### After (Decoupled)
```
Migration Script (Run Once)          Application Startup
    ↓                                     ↓
Create all tables                  Assume schema exists
    ↓                                     ↓
Verify schema                      Start serving requests
    ↓
Done
```

**Benefits:**
- Clear responsibility separation
- Predictable application behavior
- Explicit migration tracking
- Easy to add migration versioning later

---

## Migration Script: `db/migrate.py`

### Commands

#### 1. Run Migrations (Create Schema)
```bash
python db/migrate.py migrate
```

**Output:**
```
================================================================================
DATABASE MIGRATION - INITIALIZING SCHEMA
================================================================================
Database URL: sqlite:///./robot_planner.db
Creating database tables...
Successfully created 6 tables:
  ✓ walls
  ✓ obstacles
  ✓ plans
  ✓ paths
  ✓ executions
  ✓ grids
================================================================================
MIGRATION COMPLETED SUCCESSFULLY
================================================================================
```

**When to run:**
- First time setting up the project
- After deleting the database
- When deploying to a new environment

---

#### 2. Check Migration Status
```bash
python db/migrate.py status
```

**Output (if migrated):**
```
✓ All required tables exist
```

**Output (if not migrated):**
```
✗ Missing tables: {'walls', 'obstacles', 'plans'}
```

**When to run:**
- Before starting the application
- To verify database state
- In deployment scripts as a health check

---

#### 3. Drop All Tables (Danger!)
```bash
python db/migrate.py drop
```

**Interactive confirmation required:**
```
================================================================================
WARNING: DROPPING ALL TABLES
================================================================================
Are you sure you want to drop all tables? (yes/no):
```

**When to run:**
- Development/testing when you need a fresh start
- **NEVER in production without backups**

---

## Integration with Application

### Application Startup (`Server/main.py`)

**What Changed:**
```python
# BEFORE: Application managed schema
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    logger.info("Initializing database...")
    init_db()  # ← Application creates tables
    yield

# AFTER: Application assumes schema exists
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    logger.info("Note: Database tables must exist (run migrate.py first)")
    yield
```

**The application now:**
- ✅ Starts faster (no schema checks)
- ✅ Fails fast if database not initialized
- ✅ Has single responsibility (serve requests only)

---

### Automated Setup (`start.sh` / `run.sh`)

Both scripts now automatically:
1. Check if migrations have been run
2. Run migrations if needed
3. Start the application

**start.sh** (Full setup):
```bash
# ... virtual environment setup ...

# Check and run migrations
echo "Checking database migrations..."
python db/migrate.py status
if [ $? -ne 0 ]; then
    echo "Running database migrations..."
    python db/migrate.py migrate
fi

# Start server
```

**run.sh** (Quick run):
```bash
# Check if database file exists
if [ ! -f "robot_planner.db" ]; then
    echo "Database not found. Running migrations..."
    python db/migrate.py migrate
fi

# Start server
```

---

## Database Schema

### Tables Created by Migration

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `walls` | Wall geometries | id, name, geometry, created_at |
| `obstacles` | Obstacles within walls | id, wall_id, type, geometry |
| `plans` | Planning requests | id, wall_id, resolution, status |
| `paths` | Candidate paths | id, plan_id, strategy, coverage, path_data |
| `executions` | Path execution tracking | id, path_id, status, progress |
| `grids` | Cached occupancy grids | id, wall_id, resolution, grid_array |

### Relationships
```
Wall (1) ─── (N) Obstacles
     └─── (N) Plans ─── (N) Paths ─── (N) Executions
     └─── (N) Grids (cache)
```

---

## Deployment Workflows

### Development (Local)
```bash
# First time
cd Robot
./start.sh  # Auto-runs migrations

# Subsequent runs
./run.sh    # Checks if migrations needed
```

### Production (Docker)
```dockerfile
# Dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Run migrations as part of container startup
CMD python db/migrate.py migrate && \
    uvicorn main:app --host 0.0.0.0 --port 8000 --app-dir Server
```

### Production (Manual)
```bash
# Step 1: Deploy code
git pull origin main

# Step 2: Run migrations
python db/migrate.py migrate

# Step 3: Restart application
systemctl restart robot-planner
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
steps:
  - name: Checkout code
    uses: actions/checkout@v2
  
  - name: Setup Python
    uses: actions/setup-python@v2
  
  - name: Install dependencies
    run: pip install -r requirements.txt
  
  - name: Run migrations
    run: python db/migrate.py migrate
  
  - name: Run tests
    run: pytest
  
  - name: Deploy application
    run: ./deploy.sh
```

---

## Migration Best Practices

### ✅ DO:
- Run `migrate.py status` before starting app
- Keep migrations idempotent (safe to run multiple times)
- Version control your migration scripts
- Run migrations before deploying code changes
- Test migrations on staging before production
- Backup database before running `drop` command

### ❌ DON'T:
- Don't run migrations from within application code
- Don't modify schema during runtime
- Don't skip migration status checks
- Don't delete database without backups
- Don't deploy code without running migrations

---

## Troubleshooting

### Problem: "No such table: walls"
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: walls
```

**Solution:**
```bash
python db/migrate.py migrate
```

### Problem: "Table already exists"
```
sqlite3.OperationalError: table walls already exists
```

**This is actually OK!** The migration script uses `create_all()` which is idempotent. If you see this during normal operations, it means migrations have already run.

**To verify:**
```bash
python db/migrate.py status
```

### Problem: Corrupted Database
```bash
# Backup first if needed
cp robot_planner.db robot_planner.db.backup

# Drop and recreate
python db/migrate.py drop
python db/migrate.py migrate
```

### Problem: Wrong Database File Location

Check `DATABASE_URL` in your environment:
```bash
# Default: sqlite:///./robot_planner.db (current directory)
echo $DATABASE_URL

# Override:
export DATABASE_URL="sqlite:///./custom_location.db"
python db/migrate.py migrate
```

---

## Future: Alembic Integration

For production systems with evolving schemas, consider integrating [Alembic](https://alembic.sqlalchemy.org/):

```bash
# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

This provides:
- Migration versioning
- Up/down migrations
- Migration history tracking
- Schema evolution over time

---

## Summary

The decoupled migration system ensures:

1. **Separation of Concerns**: Database schema management is separate from application runtime
2. **Explicit Control**: Migrations run when you decide, not automatically
3. **Predictable Behavior**: Application startup is fast and consistent
4. **Production Ready**: Clear deployment workflow with migration gates

**Remember:**
```bash
# Always run this first (or use start.sh)
python db/migrate.py migrate

# Then start your application
./run.sh
```
