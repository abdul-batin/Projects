# Sample API Payloads - Quick Reference

## Base URL
```
http://localhost:8000
```

---

## 1. CREATE WALL

### Simple Rectangle (5m x 4m)
```bash
curl -X POST http://localhost:8000/walls \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Living Room",
    "geometry": {
      "coordinates": [[0,0], [5,0], [5,4], [0,4]]
    }
  }'
```

### L-Shaped Room
```bash
curl -X POST http://localhost:8000/walls \
  -H "Content-Type: application/json" \
  -d '{
    "name": "L-Shaped Office",
    "geometry": {
      "coordinates": [[0,0], [10,0], [10,6], [6,6], [6,10], [0,10], [0,0]]
    }
  }'
```

### Complex Shape
```bash
curl -X POST http://localhost:8000/walls \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Conference Room",
    "geometry": {
      "coordinates": [[0,0], [8,0], [8,5], [6,5], [6,7], [2,7], [2,5], [0,5], [0,0]]
    }
  }'
```

**Response:**
```json
{
  "wall_id": 1,
  "name": "Living Room",
  "geometry": {...},
  "created_at": "2026-01-18T12:00:00"
}
```

---

## 2. GET WALL

```bash
curl http://localhost:8000/walls/1
```

**Response:**
```json
{
  "wall_id": 1,
  "name": "Living Room",
  "geometry": {...},
  "obstacles": [],
  "created_at": "2026-01-18T12:00:00"
}
```

---

## 3. LIST ALL WALLS

```bash
curl http://localhost:8000/walls
```

---

## 4. ADD OBSTACLES

### Window
```bash
curl -X POST http://localhost:8000/walls/1/obstacles \
  -H "Content-Type: application/json" \
  -d '{
    "type": "window",
    "geometry": {
      "coordinates": [[1,2], [2,2], [2,3.5], [1,3.5]]
    }
  }'
```

### Door
```bash
curl -X POST http://localhost:8000/walls/1/obstacles \
  -H "Content-Type: application/json" \
  -d '{
    "type": "door",
    "geometry": {
      "coordinates": [[3.5,0], [4.5,0], [4.5,1], [3.5,1]]
    }
  }'
```

### Furniture (Desk)
```bash
curl -X POST http://localhost:8000/walls/1/obstacles \
  -H "Content-Type: application/json" \
  -d '{
    "type": "desk",
    "geometry": {
      "coordinates": [[2,2], [4,2], [4,3.5], [2,3.5]]
    }
  }'
```

### Pillar/Column
```bash
curl -X POST http://localhost:8000/walls/1/obstacles \
  -H "Content-Type: application/json" \
  -d '{
    "type": "column",
    "geometry": {
      "coordinates": [[5,2], [5.5,2], [5.5,2.5], [5,2.5]]
    }
  }'
```

**Response:**
```json
{
  "obstacle_id": 1,
  "wall_id": 1,
  "type": "window",
  "geometry": {...},
  "created_at": "2026-01-18T12:00:00"
}
```

---

## 5. LIST OBSTACLES

```bash
curl http://localhost:8000/walls/1/obstacles
```

---

## 6. GENERATE PLAN

### High Resolution (10cm)
```bash
curl -X POST http://localhost:8000/walls/1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "resolution": 0.1
  }'
```

### Medium Resolution (20cm)
```bash
curl -X POST http://localhost:8000/walls/1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "resolution": 0.2
  }'
```

### Low Resolution (50cm)
```bash
curl -X POST http://localhost:8000/walls/1/plan \
  -H "Content-Type: application/json" \
  -d '{
    "resolution": 0.5
  }'
```

**Response:**
```json
{
  "plan_id": 1,
  "wall_id": 1,
  "status": "COMPLETED",
  "best_path_id": 1,
  "candidates": [
    {
      "path_id": 1,
      "strategy": "horizontal_sweep",
      "coverage": 0.95,
      "path_length": 450,
      "turns": 20
    },
    {
      "path_id": 2,
      "strategy": "vertical_sweep",
      "coverage": 0.93,
      "path_length": 480,
      "turns": 18
    }
  ],
  "created_at": "2026-01-18T12:00:00"
}
```

---

## 7. GET PLAN DETAILS

```bash
curl http://localhost:8000/walls/plans/1
```

---

## 8. LIST ALL PLANS FOR WALL

```bash
curl http://localhost:8000/walls/1/plans
```

---

## 9. EXECUTE PATH

```bash
curl -X POST http://localhost:8000/paths/1/execute
```

**Response:**
```json
{
  "execution_id": 1,
  "path_id": 1,
  "status": "PENDING",
  "progress": 0.0,
  "started_at": "2026-01-18T12:00:00"
}
```

---

## 10. UPDATE TELEMETRY

### 25% Progress
```bash
curl -X POST http://localhost:8000/telemetry/update \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": 1,
    "position": [1.5, 2.0],
    "progress": 25.0,
    "status": "RUNNING"
  }'
```

### 50% Progress
```bash
curl -X POST http://localhost:8000/telemetry/update \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": 1,
    "position": [2.5, 2.0],
    "progress": 50.0,
    "status": "RUNNING"
  }'
```

### 100% Complete
```bash
curl -X POST http://localhost:8000/telemetry/update \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": 1,
    "position": [4.5, 3.5],
    "progress": 100.0,
    "status": "COMPLETED"
  }'
```

### Error/Failed Status
```bash
curl -X POST http://localhost:8000/telemetry/update \
  -H "Content-Type: application/json" \
  -d '{
    "execution_id": 1,
    "position": [2.0, 1.5],
    "progress": 35.0,
    "status": "FAILED"
  }'
```

---

## 11. GET CURRENT TELEMETRY

```bash
curl http://localhost:8000/telemetry/1/current
```

---

## 12. GET EXECUTION STATUS

```bash
curl http://localhost:8000/paths/executions/1
```

---

## 13. UPDATE EXECUTION STATUS (Manual)

```bash
curl -X PATCH "http://localhost:8000/paths/executions/1?status=RUNNING&progress=75.5"
```

---

## 14. LIST ALL EXECUTIONS FOR PATH

```bash
curl http://localhost:8000/paths/1/executions
```

---

## 15. DELETE WALL

```bash
curl -X DELETE http://localhost:8000/walls/1
```

---

## 16. HEALTH CHECK

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-18T12:00:00"
}
```

---

## 17. SYSTEM STATISTICS

```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "walls_count": 5,
  "obstacles_count": 12,
  "plans_count": 8,
  "paths_count": 16,
  "executions_count": 3,
  "cached_grids_count": 10
}
```

---

## Complete Workflow Example

### Step-by-Step Test Flow

```bash
# 1. Check server health
curl http://localhost:8000/health

# Note: Migrations should be run before starting server
# python db/migrate.py migrate

# 2. Create a wall (save the wall_id from response)
curl -X POST http://localhost:8000/walls \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Room", "geometry": {"coordinates": [[0,0], [5,0], [5,4], [0,4]]}}'

# 3. Add obstacle (replace {wall_id} with actual ID)
curl -X POST http://localhost:8000/walls/{wall_id}/obstacles \
  -H "Content-Type: application/json" \
  -d '{"type": "window", "geometry": {"coordinates": [[1,2], [2,2], [2,3], [1,3]]}}'

# 4. Generate plan (save plan_id and best_path_id from response)
curl -X POST http://localhost:8000/walls/{wall_id}/plan \
  -H "Content-Type: application/json" \
  -d '{"resolution": 0.1}'

# 5. Execute the best path (replace {path_id}, save execution_id)
curl -X POST http://localhost:8000/paths/{path_id}/execute

# 6. Send telemetry update (replace {execution_id})
curl -X POST http://localhost:8000/telemetry/update \
  -H "Content-Type: application/json" \
  -d '{"execution_id": {execution_id}, "position": [2.5, 2.0], "progress": 50.0, "status": "RUNNING"}'

# 7. Check execution status
curl http://localhost:8000/paths/executions/{execution_id}

# 8. View system stats
curl http://localhost:8000/stats
```

---

## Using with HTTPie (Alternative to cURL)

If you have `httpie` installed:

```bash
# Create wall
http POST :8000/walls name="Test Room" geometry:='{"coordinates": [[0,0], [5,0], [5,4], [0,4]]}'

# Add obstacle
http POST :8000/walls/1/obstacles type=window geometry:='{"coordinates": [[1,2], [2,2], [2,3], [1,3]]}'

# Generate plan
http POST :8000/walls/1/plan resolution:=0.1

# Execute path
http POST :8000/paths/1/execute

# Update telemetry
http POST :8000/telemetry/update execution_id:=1 position:='[2.5, 2.0]' progress:=50.0 status=RUNNING
```

---

## Using Python `requests`

```python
import requests

BASE_URL = "http://localhost:8000"

# Create wall
wall_response = requests.post(f"{BASE_URL}/walls", json={
    "name": "Test Room",
    "geometry": {"coordinates": [[0,0], [5,0], [5,4], [0,4]]}
})
wall_id = wall_response.json()["wall_id"]

# Add obstacle
obstacle_response = requests.post(f"{BASE_URL}/walls/{wall_id}/obstacles", json={
    "type": "window",
    "geometry": {"coordinates": [[1,2], [2,2], [2,3], [1,3]]}
})

# Generate plan
plan_response = requests.post(f"{BASE_URL}/walls/{wall_id}/plan", json={
    "resolution": 0.1
})
plan_data = plan_response.json()
path_id = plan_data["best_path_id"]

# Execute
exec_response = requests.post(f"{BASE_URL}/paths/{path_id}/execute")
execution_id = exec_response.json()["execution_id"]

# Send telemetry
telemetry_response = requests.post(f"{BASE_URL}/telemetry/update", json={
    "execution_id": execution_id,
    "position": [2.5, 2.0],
    "progress": 50.0,
    "status": "RUNNING"
})

print(f"Execution {execution_id} at 50% progress")
```

---

## Interactive API Documentation

Once the server is running, visit:

**Swagger UI:**
```
http://localhost:8000/docs
```

**ReDoc:**
```
http://localhost:8000/redoc
```

Both provide interactive API testing with auto-generated forms!
