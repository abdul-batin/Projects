# Quick Reference - Running the Robot Wall Planner

## From Robot Directory

### Option 1: Full Setup (First Time)
```bash
cd /Users/mohammedbatin/dev/Projects/Robot
./start.sh
```
This will:
- Create virtual environment
- Install dependencies
- Set PYTHONPATH
- Start server

### Option 2: Quick Run (After Setup)
```bash
cd /Users/mohammedbatin/dev/Projects/Robot
./run.sh
```
This assumes dependencies are already installed.

### Option 3: Manual Run
```bash
cd /Users/mohammedbatin/dev/Projects/Robot

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/Server"

# Run server
uvicorn Server.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 4: With Virtual Environment
```bash
cd /Users/mohammedbatin/dev/Projects/Robot
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/Server"
uvicorn Server.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

### PYTHONPATH Setup
The key is to include both:
- Current directory (Robot): `$(pwd)`
- Server directory: `$(pwd)/Server`

This allows:
- `Server/main.py` to import from `api/`, `database`, etc. (relative to Server/)
- `Server/services/planner_service.py` to import from `algorithm/` (relative to Robot/)

### Why This Works
```
Robot/                          ← In PYTHONPATH
├── Server/                     ← In PYTHONPATH
│   ├── main.py                 → imports from api, database (finds in Server/)
│   ├── api/
│   ├── database.py
│   └── services/
│       └── planner_service.py  → imports from algorithm (finds in Robot/)
└── algorithm/                  ← Found via Robot/ in PYTHONPATH
    ├── planner.py
    └── ...
```

## Configuration

### Database
By default uses SQLite: `robot_planner.db` in Robot directory

To use PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:password@localhost/robot_planner"
```

### Port
Default: 8000

To change:
```bash
uvicorn Server.main:app --port 8080
```

## Accessing the API

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError`, ensure PYTHONPATH is set:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/Server"
```

### Database Errors
Delete and recreate:
```bash
rm robot_planner.db
# Restart server - DB will be recreated
```

### Port Already in Use
Change the port:
```bash
uvicorn Server.main:app --port 8080
```
