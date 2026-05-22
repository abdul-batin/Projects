# Logging Configuration Guide

## Overview

Logging has been added to all major components of the Robot Wall Planner system using Python's built-in `logging` module.

## Configuration

Logging is configured in `Server/main.py`:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Log Levels

- **DEBUG**: Detailed diagnostic information (grid caching, A* paths, etc.)
- **INFO**: General informational messages (wall created, plan started, etc.)
- **WARNING**: Warning messages (wall not found, etc.)
- **ERROR**: Error messages with stack traces

## Logged Components

### Server Layer
- ✅ `main.py` - Application lifecycle, startup/shutdown
- ✅ `database.py` - Database initialization and connections
- ✅ `repositories.py` - Database operations (create, update, delete)

### API Layer
- ✅ `api/walls.py` - Wall and obstacle operations
- ✅ `api/planning.py` - Planning requests and responses
- ✅ `api/execution.py` - Path execution operations
- ✅ `api/telemetry.py` - Robot telemetry updates
- ✅ `api/monitoring.py` - Health and statistics

### Service Layer
- ✅ `services/planner_service.py` - Planning orchestration, grid caching

### Algorithm Layer
- ✅ `algorithm/planner.py` - Main planning coordination
- ✅ `algorithm/grid_construction.py` - Grid building operations
- ✅ `algorithm/sweep.py` - Sweep algorithms execution
- ✅ `algorithm/algorithms.py` - A* pathfinding
- ✅ `algorithm/metrics.py` - Metrics calculation

## Example Log Output

```
2026-01-18 10:15:23,456 - Server.main - INFO - Starting application...
2026-01-18 10:15:23,457 - Server.database - INFO - Initializing database with URL: sqlite:///./robot_planner.db
2026-01-18 10:15:23,500 - Server.database - INFO - Database tables created successfully
2026-01-18 10:15:23,501 - Server.main - INFO - Database initialized successfully
2026-01-18 10:15:30,123 - Server.api.walls - INFO - API: Creating wall 'Living Room'
2026-01-18 10:15:30,124 - Server.repositories - INFO - Creating wall: Living Room
2026-01-18 10:15:30,150 - Server.repositories - INFO - Wall created with ID: abc-123
2026-01-18 10:15:30,151 - Server.api.walls - INFO - API: Wall created successfully with ID abc-123
2026-01-18 10:15:35,200 - Server.api.planning - INFO - API: Planning wall abc-123 with resolution 0.1
2026-01-18 10:15:35,201 - Server.services.planner_service - INFO - PlannerService: Starting plan for wall abc-123 with resolution 0.1
2026-01-18 10:15:35,202 - Server.repositories - INFO - Creating plan for wall abc-123 with resolution 0.1
2026-01-18 10:15:35,220 - Server.services.planner_service - DEBUG - PlannerService: Checking grid cache for wall abc-123
2026-01-18 10:15:35,221 - Server.services.planner_service - INFO - PlannerService: Building new grid for wall abc-123
2026-01-18 10:15:35,222 - algorithm.grid_construction - INFO - GridConstruction: Building grid of size 50x50 with resolution 0.1
2026-01-18 10:15:35,300 - Server.services.planner_service - INFO - PlannerService: Grid built with shape (50, 50)
2026-01-18 10:15:35,305 - Server.services.planner_service - INFO - PlannerService: Running planning algorithms
2026-01-18 10:15:35,306 - algorithm.planner - INFO - Planning: Starting path planning for grid of shape (50, 50)
2026-01-18 10:15:35,307 - algorithm.sweep - DEBUG - Sweep: Starting horizontal sweep on 50x50 grid
2026-01-18 10:15:35,400 - algorithm.planner - INFO - Planning: horizontal strategy - coverage: 98.50%, length: 2450
2026-01-18 10:15:35,401 - algorithm.sweep - DEBUG - Sweep: Starting vertical sweep on 50x50 grid
2026-01-18 10:15:35,500 - algorithm.planner - INFO - Planning: vertical strategy - coverage: 96.20%, length: 2400
2026-01-18 10:15:35,501 - Server.services.planner_service - INFO - PlannerService: Planning complete with 2 candidates
2026-01-18 10:15:35,550 - Server.services.planner_service - INFO - PlannerService: Plan def-456 completed successfully. Best path: ghi-789
```

## Changing Log Level

### Application-wide
Edit `Server/main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # Show all logs
logging.basicConfig(level=logging.WARNING)  # Only warnings and errors
```

### Per-module
Add after logger initialization:
```python
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # This module only
```

### Via Environment Variable
```bash
export LOG_LEVEL=DEBUG
uvicorn Server.main:app --log-level debug
```

## Writing to File

Modify `Server/main.py`:
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('robot_planner.log'),
        logging.StreamHandler()  # Also print to console
    ]
)
```

## Filtering Logs

### View only errors
```bash
./run.sh 2>&1 | grep ERROR
```

### View specific module
```bash
./run.sh 2>&1 | grep "algorithm.planner"
```

### View planning operations
```bash
./run.sh 2>&1 | grep "Planning"
```

## Best Practices

1. **Use appropriate levels**:
   - DEBUG: Detailed diagnostic (grid cache hits, path details)
   - INFO: Important operations (wall created, plan started)
   - WARNING: Unexpected but handled (wall not found)
   - ERROR: Errors that need attention (plan failed)

2. **Include context**:
   - IDs (wall_id, plan_id, path_id)
   - Key metrics (coverage, resolution)
   - Operation results

3. **Use structured logging**:
   - Prefix with component name (API, Service, Algorithm)
   - Include operation being performed
   - Add relevant data for debugging

## Monitoring in Production

For production monitoring, consider:
- **Log aggregation** (ELK stack, Splunk)
- **Alerting** on ERROR logs
- **Metrics** extraction from logs
- **Structured JSON** logging format

Example JSON logging:
```python
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'module': record.name,
            'message': record.getMessage()
        })

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.root.addHandler(handler)
```
