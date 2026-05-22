# System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                            CLIENT (Browser/App)                            │
└────────────────────────────────┬──────────────────────────────────────────┘
                                 │ HTTP/REST
                                 ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI APPLICATION                                │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                       API ENDPOINTS                               │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐             │    │
│  │  │   Walls     │  │   Planning   │  │ Execution  │             │    │
│  │  │  /walls     │  │ /walls/{id}  │  │ /paths/    │             │    │
│  │  │  /obstacles │  │    /plan     │  │  /execute  │             │    │
│  │  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘             │    │
│  │         │                │                 │                     │    │
│  │  ┌──────┴────────┐  ┌───┴────────┐  ┌────┴──────┐             │    │
│  │  │  Telemetry    │  │ Monitoring │  │    Root   │             │    │
│  │  │  /telemetry   │  │   /health  │  │     /     │             │    │
│  │  │   /update     │  │   /stats   │  │           │             │    │
│  │  └───────────────┘  └────────────┘  └───────────┘             │    │
│  └──────────────────────────────┬────────────────────────────────┘    │
│                                  │                                      │
│  ┌──────────────────────────────┴────────────────────────────────┐    │
│  │                      SERVICE LAYER                             │    │
│  │                                                                 │    │
│  │           ┌─────────────────────────────────┐                  │    │
│  │           │     PlannerService               │                  │    │
│  │           │  • Orchestrates planning         │                  │    │
│  │           │  • Manages grid caching          │                  │    │
│  │           │  • Coordinates algorithms        │                  │    │
│  │           └─────────────┬───────────────────┘                  │    │
│  └─────────────────────────┼──────────────────────────────────────┘    │
│                             │                                           │
│  ┌─────────────────────────┴──────────────────────────────────────┐    │
│  │                   REPOSITORY LAYER                              │    │
│  │                                                                  │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │    │
│  │  │   Wall   │ │ Obstacle │ │   Plan   │ │   Path   │          │    │
│  │  │   Repo   │ │   Repo   │ │   Repo   │ │   Repo   │          │    │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │    │
│  │       │            │            │            │                  │    │
│  │  ┌────┴─────┐ ┌───┴─────┐                                      │    │
│  │  │Execution │ │  Grid   │                                      │    │
│  │  │   Repo   │ │  Repo   │                                      │    │
│  │  └────┬─────┘ └────┬────┘                                      │    │
│  └───────┼────────────┼──────────────────────────────────────────┘    │
│          │            │                                                │
│  ┌───────┴────────────┴──────────────────────────────────────────┐    │
│  │                    DATABASE LAYER                              │    │
│  │                                                                 │    │
│  │    ┌────────────────────────────────────────────────────┐     │    │
│  │    │         SQLAlchemy Session (db/database.py)           │     │    │
│  │    │  • Session factory & management                    │     │    │
│  │    │  • Connection pooling                              │     │    │
│  │    │  • Dependency injection                            │     │    │
│  │    └────────────────┬───────────────────────────────────┘     │    │
│  │                     │                                          │    │
│  │    ┌────────────────┴───────────────────────────────────┐     │    │
│  │    │    Database Migrations (db/migrate.py)             │     │    │
│  │    │  • Schema initialization (run once)                │     │    │
│  │    │  • Table creation & verification                   │     │    │
│  │    │  • Migration status checks                         │     │    │
│  │    └────────────────┬───────────────────────────────────┘     │    │
│  │                     │                                          │    │
│  └─────────────────────┼──────────────────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                         DATABASE (PostgreSQL)                       │
│                                                                            │
│  ┌─────────┐  ┌────────────┐  ┌───────┐  ┌───────┐  ┌────────────┐     │
│  │  walls  │  │ obstacles  │  │ plans │  │ paths │  │ executions │     │
│  ├─────────┤  ├────────────┤  ├───────┤  ├───────┤  ├────────────┤     │
│  │ id      │  │ id         │  │ id    │  │ id    │  │ id         │     │
│  │ name    │  │ wall_id FK │  │wall_id│  │plan_id│  │ path_id FK │     │
│  │ geometry│  │ type       │  │resol..│  │strat..│  │ status     │     │
│  │ ...     │  │ geometry   │  │status │  │cover..│  │ progress   │     │
│  └────┬────┘  └─────┬──────┘  │best_..│  │path_..│  │ ...        │     │
│       │             │          └───┬───┘  └───┬───┘  └────────────┘     │
│       │             │              │          │                          │
│       │             └──────────────┘          │                          │
│       └────────────────────────────────────────                          │
│                                                                            │
│  ┌─────────┐  (Grid Cache)                                               │
│  │  grids  │                                                              │
│  ├─────────┤                                                              │
│  │ id      │                                                              │
│  │wall_id  │                                                              │
│  │resolution│                                                             │
│  │grid_data│                                                              │
│  └─────────┘                                                              │
└───────────────────────────────────────────────────────────────────────────┘

                              │
                              │ Uses
                              ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          ALGORITHM LAYER                                   │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                    Grid Construction                              │    │
│  │  • Converts Polygon geometry to occupancy grid                    │    │
│  │  • 0 = free space, 1 = occupied/obstacle                          │    │
│  │  • Uses Shapely for geometric operations                          │    │
│  └────────────────────────────┬─────────────────────────────────────┘    │
│                                │                                           │
│  ┌────────────────────────────┴─────────────────────────────────────┐    │
│  │                     Path Planner                                  │    │
│  │  • Coordinates sweep strategies and pathfinding                   │    │
│  │  • Evaluates multiple candidates                                  │    │
│  │  • Returns best path based on coverage                            │    │
│  └────────────┬───────────────────────────────┬─────────────────────┘    │
│               │                                │                           │
│  ┌────────────┴─────────────┐    ┌───────────┴──────────────┐            │
│  │   Sweep Algorithms       │    │    A* Pathfinding         │            │
│  │  • Horizontal sweep      │    │  • Connects segments      │            │
│  │  • Vertical sweep        │    │  • Manhattan distance     │            │
│  │  • Alternating direction │    │  • 4-way connectivity     │            │
│  └──────────────────────────┘    └───────────────────────────┘            │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                        Metrics                                    │    │
│  │  • Coverage percentage                                            │    │
│  │  • Path length                                                    │    │
│  │  • Quality scoring                                                │    │
│  └──────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────┘


DATA FLOW EXAMPLE: Create Wall and Generate Plan
═══════════════════════════════════════════════════

1. Client → POST /walls
   {name: "Wall A", geometry: [[0,0],[10,0],[10,5],[0,5]]}
                │
                ▼
2. Walls API → WallRepository.create_wall()
                │
                ▼
3. Database ← INSERT INTO walls (id, name, geometry, ...)
                │
                ▼
4. Client ← {wall_id: "abc-123"}

5. Client → POST /walls/abc-123/plan {resolution: 0.1}
                │
                ▼
6. Planning API → PlannerService.run_plan()
                │
                ├──→ GridRepository.get_or_create_grid()
                │    • Check cache
                │    • If miss: Build grid from geometry
                │    • Store in grids table
                │
                ├──→ Algorithm.plan(grid)
                │    • Horizontal sweep → candidate 1
                │    • Vertical sweep → candidate 2
                │    • A* to connect segments
                │    • Compute metrics
                │
                └──→ Store results
                     • Create Plan record
                     • Create Path records (all candidates)
                     • Update Plan.best_path_id
                │
                ▼
7. Client ← {
     plan_id: "def-456",
     best_path_id: "ghi-789",
     candidates: [
       {path_id: "ghi-789", coverage: 0.98, path_length: 450},
       {path_id: "jkl-012", coverage: 0.96, path_length: 420}
     ]
   }


EXECUTION FLOW
═══════════════

1. Client → POST /paths/ghi-789/execute
                │
                ▼
2. Execution API → Create Execution record
                │  Update Path.execution_status = RUNNING
                │
                ▼
3. Robot ← (Future: Message via broker)
                │
                ▼
4. Robot → POST /telemetry/update
           {execution_id, position, progress: 45.5, status: RUNNING}
                │
                ▼
5. Telemetry API → Update Execution.progress
                │
                ▼
6. Monitoring Dashboard ← GET /executions/{id}
                          {progress: 45.5%, status: RUNNING}
```

## Key Design Patterns

### Repository Pattern
- Abstracts database operations
- Easy to test with mocks
- Database-agnostic

### Service Layer
- Business logic separated from API
- Coordinates multiple repositories
- Handles caching strategy

### Dependency Injection
- FastAPI's `Depends()` for DB sessions
- Clean separation of concerns
- Easy to swap implementations

### Caching Strategy
- Grid computation is expensive
- Cache by (wall_id, resolution)
- Invalidate on obstacle changes

### Status Tracking
```
Plan:      PENDING → COMPLETED/FAILED
Path:      NOT_STARTED → RUNNING → COMPLETED/FAILED
Execution: SENT → RUNNING → COMPLETED/FAILED
```
