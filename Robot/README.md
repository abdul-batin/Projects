# Autonomous Wall Planner API

A FastAPI-based system for planning and executing robot wall coverage paths. The system generates optimal paths for robots to cover wall surfaces while avoiding obstacles.

## Architecture

### Components

- **Server Layer** (FastAPI)
  - `main.py`: Main application entry point with lifespan management
  - `models.py`: Pydantic models for API request/response validation
  - `api/`: API endpoint routers
  - `services/`: Business logic services

- **Database Layer** (`db/`)
  - `database.py`: SQLAlchemy configuration and session management
  - `migrate.py`: Database migration script (decoupled from runtime)
  - `models.py`: ORM models for Wall, Obstacle, Plan, Path, Execution, Grid
  - `repositories.py`: Data access layer for database operations

- **API Endpoints**
  - `/walls`: Wall and obstacle management
  - `/walls/{wall_id}/plan`: Path planning
  - `/paths/{path_id}/execute`: Path execution
  - `/telemetry`: Robot telemetry updates
  - `/health`, `/stats`: Monitoring

- **Services Layer**
  - `planner_service.py`: Orchestrates planning with grid caching

- **Algorithm Layer**
  - `grid_construction.py`: Converts polygons to occupancy grids
  - `planner.py`: Coordinates sweep and pathfinding algorithms
  - `sweep.py`: Horizontal and vertical sweep strategies
  - `algorithms.py`: A* pathfinding for segment connections
  - `metrics.py`: Coverage and path length calculations

### Database Schema

- **walls**: Physical walls to be covered (name, geometry)
- **obstacles**: Obstacles within walls (type, geometry)
- **plans**: Planning operations (resolution, status, best_path_id)
- **paths**: Candidate paths from planning (strategy, coverage, path_data)
- **executions**: Execution attempts (status, progress, timestamps)
- **grids**: Cached occupancy grids (resolution, grid_data)

Relationships:
- Wall → many Obstacles, Plans
- Plan → many Paths
- Path → many Executions

## Setup

### Prerequisites

- Python 3.12+
- Virtual environment recommended

### Installation

```bash
# Navigate to Robot directory
cd Robot

# Option 1: Use automated setup script (recommended)
./start.sh

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database (first time only)
python db/migrate.py migrate
```

### Environment Variables

Create a `.env` file (optional):

```env
DATABASE_URL=sqlite:///./robot_planner.db  # Default if not set
```

For PostgreSQL:
```env
DATABASE_URL=postgresql://user:password@localhost/robot_planner
```

## Running the Application

### Quick Start (Recommended)

```bash
# First time or after clean install
./start.sh

# Subsequent runs
./run.sh
```

### Manual Startup

```bash
# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/Server"

# Run migrations (if not done)
python db/migrate.py migrate

# Start server
cd Server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
cd Server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Management

```bash
# Check migration status
python db/migrate.py status

# Run migrations
python db/migrate.py migrate

# Reset database (WARNING: deletes all data)
python db/migrate.py drop
```

## API Usage

### 1. Create a Wall

```bash
curl -X POST "http://localhost:8000/walls" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Living Room Wall",
    "geometry": {
      "coordinates": [[0,0], [5,0], [5,3], [0,3]]
    }
  }'
```

Response: `{"wall_id": "uuid-here"}`

### 2. Add Obstacles

```bash
curl -X POST "http://localhost:8000/walls/{wall_id}/obstacles" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "window",
    "geometry": {
      "coordinates": [[1,1], [2,1], [2,2], [1,2]]
    }
  }'
```

### 3. Generate Plan

```bash
curl -X POST "http://localhost:8000/walls/{wall_id}/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "resolution": 0.1
  }'
```

Response includes `plan_id`, `best_path_id`, and coverage metrics for all candidates.

### 4. Execute Path

```bash
curl -X POST "http://localhost:8000/paths/{path_id}/execute"
```

Response: `{"status": "SENT", "execution_id": "uuid"}`

### 5. Monitor Execution

```bash
# Get execution status
curl "http://localhost:8000/paths/executions/{execution_id}"

# Update execution status (from robot/monitoring service)
curl -X PATCH "http://localhost:8000/paths/executions/{execution_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "RUNNING",
    "progress": 45.5
  }'
```

## Development

### Database Migrations

The database is automatically initialized on startup. To reset:

```bash
rm robot_planner.db  # Delete existing database
# Restart the application - tables will be recreated
```

### Running Tests

```bash
pytest tests/  # TODO: Add tests
```

### Code Structure

```
Robot/
├── Server/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # DB configuration
│   ├── db_models.py         # SQLAlchemy ORM models
│   ├── repositories.py      # Data access layer
│   ├── models.py            # Pydantic schemas
│   ├── api/                 # API endpoints
│   │   ├── walls.py         # Wall/obstacle management
│   │   ├── planning.py      # Path planning
│   │   ├── execution.py     # Path execution
│   │   ├── telemetry.py     # Robot telemetry
│   │   └── monitoring.py    # Health/stats
│   └── services/
│       └── planner_service.py  # Planning orchestration
├── algorithm/
│   ├── grid_construction.py # Polygon → grid conversion
│   ├── planner.py          # Main planning coordinator
│   ├── sweep.py            # Sweep algorithms
│   ├── algorithms.py       # A* pathfinding
│   └── metrics.py          # Coverage metrics
└── requirements.txt
```

## Key Concepts

### Grid Construction

Walls and obstacles (defined as polygons) are rasterized into occupancy grids where:
- `0` = free space
- `1` = occupied/obstacle

### Planning Strategies

The planner evaluates multiple strategies:
- **Horizontal Sweep**: Left-to-right, alternating directions
- **Vertical Sweep**: Top-to-bottom, alternating directions

A* pathfinding connects sweep segments.

### Grid Caching

Grids are cached in the database by `(wall_id, resolution)`. Cache is invalidated when obstacles are added/removed.

## TODO / Future Enhancements

- [ ] Message broker integration (RabbitMQ/Redis Pub/Sub) for real-time execution
- [ ] WebSocket support for live telemetry streaming
- [ ] Additional sweep strategies (spiral, zigzag)
- [ ] Multi-robot coordination
- [ ] Visualization dashboard
- [ ] Unit and integration tests
- [ ] Docker containerization
- [ ] API authentication/authorization
- [ ] Rate limiting
- [ ] Logging and metrics (Prometheus/Grafana)

## Troubleshooting

### Database Connection Issues

If using PostgreSQL and getting connection errors:
- Ensure PostgreSQL is running
- Check DATABASE_URL format
- Install psycopg2: `pip install psycopg2-binary`

### Import Errors

Make sure you're running from the correct directory:
```bash
cd Server
python -m uvicorn main:app
```

### Grid Construction Errors

- Ensure geometry coordinates form a valid closed polygon
- Check that obstacle polygons are within wall boundaries
- Verify resolution is not too small (avoid huge grids)

## License

MIT License (or specify your license)

## Contact

[Your contact information]
