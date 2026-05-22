# Test Scenarios - Robot Wall Planner

## Quick Start

### 1. Start the Server
```bash
cd /Users/mohammedbatin/dev/Projects/Robot
./run.sh
```

### 2. Run All Test Scenarios (in another terminal)
```bash
cd /Users/mohammedbatin/dev/Projects/Robot
python test_scenarios.py
```

---

## Scenario Details

### 📍 SCENARIO 1: Small Living Room (5m x 4m)

**Wall Dimensions:** 5 meters × 4 meters rectangular room

**Flow:**
1. ✅ Create wall
2. ✅ Get wall details
3. ✅ Add window obstacle (1.5m × 1m)
4. ✅ Add door obstacle (1m × 1m)
5. ✅ List all obstacles
6. ✅ Generate coverage plan (10cm resolution)
7. ✅ View plan details
8. ✅ Execute best path
9. ✅ Send telemetry updates (25%, 50%, 75%, 100%)
10. ✅ Get execution status
11. ✅ List all executions

**Input Data:**

**Wall:**
```json
{
  "name": "Living Room",
  "geometry": {
    "coordinates": [
      [0, 0], [5, 0], [5, 4], [0, 4]
    ]
  }
}
```

**Window Obstacle:**
```json
{
  "type": "window",
  "geometry": {
    "coordinates": [
      [1, 2], [2, 2], [2, 3.5], [1, 3.5]
    ]
  }
}
```

**Door Obstacle:**
```json
{
  "type": "door",
  "geometry": {
    "coordinates": [
      [3.5, 0], [4.5, 0], [4.5, 1], [3.5, 1]
    ]
  }
}
```

**Plan Request:**
```json
{
  "resolution": 0.1
}
```

---

### 📍 SCENARIO 2: Large L-Shaped Office (10m × 10m)

**Wall Dimensions:** L-shaped office space (approximately 76 square meters)

**Flow:**
1. ✅ Create L-shaped wall
2. ✅ Add desk obstacle (2m × 1.5m)
3. ✅ Add filing cabinet (1.5m × 1m)
4. ✅ Add plant decoration (1m × 1m)
5. ✅ List all obstacles
6. ✅ Generate first plan (20cm resolution)
7. ✅ Generate second plan (15cm resolution - different)
8. ✅ List all plans for wall
9. ✅ Execute best path
10. ✅ Update execution status manually
11. ✅ Get current telemetry

**Input Data:**

**Wall (L-Shape):**
```json
{
  "name": "L-Shaped Office",
  "geometry": {
    "coordinates": [
      [0, 0], [10, 0], [10, 6],
      [6, 6], [6, 10], [0, 10], [0, 0]
    ]
  }
}
```

**Desk Obstacle:**
```json
{
  "type": "desk",
  "geometry": {
    "coordinates": [
      [2, 2], [4, 2], [4, 3.5], [2, 3.5]
    ]
  }
}
```

**Filing Cabinet:**
```json
{
  "type": "filing_cabinet",
  "geometry": {
    "coordinates": [
      [7, 1], [8.5, 1], [8.5, 2], [7, 2]
    ]
  }
}
```

**Plant:**
```json
{
  "type": "plant",
  "geometry": {
    "coordinates": [
      [1, 7], [2, 7], [2, 8], [1, 8]
    ]
  }
}
```

**Plan Requests:**
```json
// First plan
{"resolution": 0.2}

// Second plan
{"resolution": 0.15}
```

---

## Manual Testing with cURL

### Scenario 1 Commands:

```bash
# 1. Create wall
curl -X POST http://localhost:8000/walls \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Living Room",
    "geometry": {
      "coordinates": [[0,0],[5,0],[5,4],[0,4]]
    }
  }'

# Save the wall_id from response, then:

# 2. Add window
curl -X POST http://localhost:8000/walls/{WALL_ID}/obstacles \
  -H "Content-Type: application/json" \
  -d '{
    "type": "window",
    "geometry": {
      "coordinates": [[1,2],[2,2],[2,3.5],[1,3.5]]
    }
  }'

# 3. Add door
curl -X POST http://localhost:8000/walls/{WALL_ID}/obstacles \
  -H "Content-Type: application/json" \
  -d '{
    "type": "door",
    "geometry": {
      "coordinates": [[3.5,0],[4.5,0],[4.5,1],[3.5,1]]
    }
  }'

# 4. Generate plan
curl -X POST http://localhost:8000/walls/{WALL_ID}/plan \
  -H "Content-Type: application/json" \
  -d '{"resolution": 0.1}'

# 5. Execute path
curl -X POST http://localhost:8000/paths/{PATH_ID}/execute

# 6. Update telemetry
curl -X POST http://localhost:8000/telemetry/update \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": "{EXECUTION_ID}",
    "position": [2.5, 2.0],
    "progress": 50.0,
    "status": "RUNNING"
  }'

# 7. Check status
curl http://localhost:8000/paths/executions/{EXECUTION_ID}
```

---

## Expected Results

### Scenario 1 Expected Output:
- **Coverage:** ~95-98% (some areas blocked by window/door)
- **Path Length:** ~400-500 cells (at 0.1m resolution)
- **Strategies:** 2 candidates (horizontal, vertical)
- **Best Strategy:** Higher coverage strategy selected automatically

### Scenario 2 Expected Output:
- **Coverage:** ~92-96% (L-shape + multiple obstacles)
- **Path Length:** ~1900-2200 cells (at 0.2m resolution)
- **Strategies:** 2 candidates evaluated
- **Multiple Plans:** Both 0.2m and 0.15m resolution plans stored

---

## API Endpoints Tested

✅ **Walls API:**
- POST `/walls` - Create wall
- GET `/walls/{wall_id}` - Get wall details
- GET `/walls` - List all walls
- POST `/walls/{wall_id}/obstacles` - Add obstacle
- GET `/walls/{wall_id}/obstacles` - List obstacles

✅ **Planning API:**
- POST `/walls/{wall_id}/plan` - Generate plan
- GET `/walls/{wall_id}/plans` - List plans
- GET `/walls/plans/{plan_id}` - Get plan details

✅ **Execution API:**
- POST `/paths/{path_id}/execute` - Execute path
- GET `/paths/{path_id}/executions` - List executions
- GET `/paths/executions/{execution_id}` - Get status
- PATCH `/paths/executions/{execution_id}` - Update status

✅ **Telemetry API:**
- POST `/telemetry/update` - Send telemetry
- GET `/telemetry/{execution_id}/current` - Get current

✅ **Monitoring API:**
- GET `/health` - Health check
- GET `/stats` - System statistics

---

## Viewing Results

### 1. Interactive API Docs
```
http://localhost:8000/docs
```
You can try all endpoints interactively here!

### 2. Check Database
```bash
# View database content
sqlite3 robot_planner.db

# List tables
.tables

# View walls
SELECT * FROM walls;

# View plans
SELECT * FROM plans;

# View paths with metrics
SELECT id, strategy, coverage, path_length FROM paths;
```

### 3. Check Logs
The application logs show detailed information:
- Grid construction
- Planning algorithm execution
- Coverage calculations
- Execution tracking

---

## Troubleshooting

### Server Not Running
```bash
cd /Users/mohammedbatin/dev/Projects/Robot
./run.sh
```

### Import Errors
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/Server"
```

### Check Server Status
```bash
curl http://localhost:8000/health
```

### View Logs in Real-time
```bash
./run.sh 2>&1 | grep -E "INFO|ERROR|Planning"
```

---

## Next Steps

After running these scenarios, you can:

1. **Modify geometries** - Try different wall shapes
2. **Add more obstacles** - Test complex scenarios
3. **Change resolutions** - See effect on coverage/performance
4. **Compare strategies** - Analyze horizontal vs vertical
5. **Monitor performance** - Check grid caching effectiveness

Enjoy testing! 🤖
