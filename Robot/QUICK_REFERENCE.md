# Quick Reference Guide - Robot Wall Planner

## 🚀 Start Server

```bash
# Option 1: Using startup script
./start.sh

# Option 2: Manual
cd Server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Docker
docker-compose up
```

## 📡 API Endpoints

### Walls
```bash
# Create wall
POST /walls
{
  "name": "Kitchen Wall",
  "geometry": {"coordinates": [[0,0],[10,0],[10,5],[0,5]]}
}

# Get wall
GET /walls/{wall_id}

# List all walls
GET /walls

# Delete wall
DELETE /walls/{wall_id}
```

### Obstacles
```bash
# Add obstacle
POST /walls/{wall_id}/obstacles
{
  "type": "window",
  "geometry": {"coordinates": [[2,1],[4,1],[4,3],[2,3]]}
}

# List obstacles
GET /walls/{wall_id}/obstacles
```

### Planning
```bash
# Generate plan
POST /walls/{wall_id}/plan
{
  "resolution": 0.1
}

# List plans for wall
GET /walls/{wall_id}/plans

# Get plan details
GET /plans/{plan_id}
```

### Execution
```bash
# Execute path
POST /paths/{path_id}/execute

# Get execution status
GET /executions/{execution_id}

# Update execution (from robot)
PATCH /executions/{execution_id}
{
  "status": "RUNNING",
  "progress": 45.5
}

# List path executions
GET /paths/{path_id}/executions
```

### Telemetry
```bash
# Send telemetry update
POST /telemetry/update
{
  "execution_id": "uuid",
  "position": [2.5, 3.1],
  "progress": 45.5,
  "status": "RUNNING"
}

# Get current telemetry
GET /telemetry/{execution_id}/current
```

### Monitoring
```bash
# Health check
GET /health

# System stats
GET /stats
```

## 🗄️ Database Models

### Wall
```python
{
  "id": "uuid",
  "name": "string",
  "geometry": [[x,y], [x,y], ...],
  "created_at": "timestamp"
}
```

### Obstacle
```python
{
  "id": "uuid",
  "wall_id": "uuid",
  "type": "window|door|furniture",
  "geometry": [[x,y], [x,y], ...],
  "created_at": "timestamp"
}
```

### Plan
```python
{
  "id": "uuid",
  "wall_id": "uuid",
  "resolution": 0.1,
  "best_path_id": "uuid",
  "status": "PENDING|COMPLETED|FAILED",
  "created_at": "timestamp"
}
```

### Path
```python
{
  "id": "uuid",
  "plan_id": "uuid",
  "strategy": "horizontal|vertical",
  "path_data": [(r,c), (r,c), ...],
  "coverage": 0.95,
  "path_length": 450,
  "execution_status": "NOT_STARTED|RUNNING|COMPLETED|FAILED"
}
```

### Execution
```python
{
  "id": "uuid",
  "path_id": "uuid",
  "status": "SENT|RUNNING|COMPLETED|FAILED",
  "progress": 45.5,
  "started_at": "timestamp",
  "completed_at": "timestamp",
  "error_message": "string"
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Database URL (optional, default: SQLite)
export DATABASE_URL="sqlite:///./robot_planner.db"

# For PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost/robot_planner"
```

### Config File (config.ini)
```ini
[database]
url = sqlite:///./robot_planner.db
pool_size = 5

[server]
host = 0.0.0.0
port = 8000
workers = 4

[planning]
default_resolution = 0.1
enable_grid_caching = true
```

## 📁 Project Structure

```
Robot/
├── Server/               # API server
│   ├── main.py          # FastAPI app
│   ├── database.py      # DB config
│   ├── db_models.py     # ORM models
│   ├── repositories.py  # Data access
│   ├── models.py        # Pydantic schemas
│   ├── api/            # Endpoints
│   └── services/       # Business logic
├── algorithm/          # Path planning
│   ├── planner.py      # Main coordinator
│   ├── sweep.py        # Sweep strategies
│   ├── algorithms.py   # A* pathfinding
│   ├── grid_construction.py
│   └── metrics.py
├── requirements.txt
├── start.sh           # Quick start
├── test_api.py        # Test suite
└── README.md
```

## 🐛 Debugging

### Check Server Status
```bash
curl http://localhost:8000/health
```

### View Database
```bash
# Install sqlite3
sqlite3 Server/robot_planner.db

# List tables
.tables

# Query walls
SELECT * FROM walls;

# Exit
.quit
```

### Check Logs
```bash
# Server logs appear in terminal where uvicorn is running
# Look for:
# - Database initialization messages
# - SQL queries (when echo=True)
# - API request logs
```

## 🧪 Test Workflow

```python
# test_api.py demonstrates this flow:

1. Create wall
   POST /walls → wall_id

2. Add obstacle  
   POST /walls/{wall_id}/obstacles → obstacle_id

3. Generate plan
   POST /walls/{wall_id}/plan → plan_id, best_path_id

4. Execute path
   POST /paths/{best_path_id}/execute → execution_id

5. Monitor
   GET /executions/{execution_id}
   GET /stats
```

## 💡 Common Tasks

### Reset Database
```bash
rm Server/robot_planner.db
# Restart server - tables will be recreated
```

### Add New Sweep Strategy
1. Add method to `algorithm/sweep.py`
2. Update `sweep_methods` dict in `algorithm/planner.py`

### Change Resolution
```python
# Lower resolution = larger grid cells = faster but less precise
resolution = 0.2  # Default: 0.1

# Higher resolution = smaller grid cells = slower but more precise
resolution = 0.05
```

### View API Docs
```
http://localhost:8000/docs  # Swagger UI (interactive)
http://localhost:8000/redoc # ReDoc (documentation)
```

## 🔐 Production Considerations

### Security
- [ ] Add authentication (JWT/OAuth)
- [ ] Enable HTTPS
- [ ] Validate input geometry
- [ ] Rate limiting

### Performance
- [ ] Use PostgreSQL for production
- [ ] Add connection pooling
- [ ] Enable Redis for caching
- [ ] Add indexes to database

### Monitoring
- [ ] Add structured logging
- [ ] Set up Prometheus metrics
- [ ] Add APM (Application Performance Monitoring)
- [ ] Health checks for dependencies

### Deployment
```bash
# Docker production
docker build -t robot-planner .
docker run -p 8000:8000 -v $(pwd)/data:/app/data robot-planner

# With PostgreSQL
docker-compose up -d
```

## 📚 Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Shapely Docs: https://shapely.readthedocs.io
- API Docs: http://localhost:8000/docs
