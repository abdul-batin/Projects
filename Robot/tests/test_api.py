"""Unit tests for API endpoints."""
import pytest


class TestWallsAPI:
    """Tests for Walls API endpoints."""
    
    def test_create_wall(self, client, sample_wall_data):
        """Test creating a wall."""
        response = client.post("/walls", json=sample_wall_data)
        assert response.status_code == 200
        data = response.json()
        assert "wall_id" in data
        assert data["wall_id"] is not None
    
    def test_get_wall(self, client, sample_wall_data):
        """Test getting a wall by ID."""
        # Create wall
        create_response = client.post("/walls", json=sample_wall_data)
        wall_id = create_response.json()["wall_id"]
        
        # Get wall
        response = client.get(f"/walls/{wall_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["wall_id"] == wall_id
        assert data["name"] == "Test Wall"
        assert len(data["geometry"]) == 4
    
    def test_get_nonexistent_wall(self, client):
        """Test getting a wall that doesn't exist."""
        response = client.get("/walls/nonexistent-id")
        assert response.status_code == 404
    
    def test_list_walls(self, client, sample_wall_data):
        """Test listing all walls."""
        # Create multiple walls
        client.post("/walls", json=sample_wall_data)
        client.post("/walls", json={**sample_wall_data, "name": "Wall 2"})
        
        # List walls
        response = client.get("/walls")
        assert response.status_code == 200
        data = response.json()
        assert "walls" in data
        assert len(data["walls"]) >= 2
    
    def test_delete_wall(self, client, sample_wall_data):
        """Test deleting a wall."""
        # Create wall
        create_response = client.post("/walls", json=sample_wall_data)
        wall_id = create_response.json()["wall_id"]
        
        # Delete wall
        response = client.delete(f"/walls/{wall_id}")
        assert response.status_code == 200
        
        # Verify deleted
        get_response = client.get(f"/walls/{wall_id}")
        assert get_response.status_code == 404
    
    def test_create_obstacle(self, client, sample_wall_data, sample_obstacle_data):
        """Test creating an obstacle for a wall."""
        # Create wall
        create_response = client.post("/walls", json=sample_wall_data)
        wall_id = create_response.json()["wall_id"]
        
        # Create obstacle
        response = client.post(f"/walls/{wall_id}/obstacles", json=sample_obstacle_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert "obstacle_id" in data
    
    def test_get_obstacles(self, client, sample_wall_data, sample_obstacle_data):
        """Test getting obstacles for a wall."""
        # Create wall
        create_response = client.post("/walls", json=sample_wall_data)
        wall_id = create_response.json()["wall_id"]
        
        # Create obstacles
        client.post(f"/walls/{wall_id}/obstacles", json=sample_obstacle_data)
        client.post(f"/walls/{wall_id}/obstacles", json={**sample_obstacle_data, "type": "door"})
        
        # Get obstacles
        response = client.get(f"/walls/{wall_id}/obstacles")
        assert response.status_code == 200
        data = response.json()
        assert "obstacles" in data
        assert len(data["obstacles"]) == 2


class TestPlanningAPI:
    """Tests for Planning API endpoints."""
    
    def test_plan_wall(self, client, sample_wall_data, sample_plan_request):
        """Test generating a plan for a wall."""
        # Create wall
        create_response = client.post("/walls", json=sample_wall_data)
        wall_id = create_response.json()["wall_id"]
        
        # Generate plan
        response = client.post(f"/walls/{wall_id}/plan", json=sample_plan_request)
        assert response.status_code == 200
        data = response.json()
        assert "plan_id" in data
        assert "best_path_id" in data
        assert "candidates" in data
        assert len(data["candidates"]) > 0
        
        # Verify candidates have required fields
        for candidate in data["candidates"]:
            assert "path_id" in candidate
            assert "coverage" in candidate
            assert "path_length" in candidate
    
    def test_plan_nonexistent_wall(self, client, sample_plan_request):
        """Test planning for a wall that doesn't exist."""
        response = client.post("/walls/nonexistent-id/plan", json=sample_plan_request)
        assert response.status_code == 404
    
    def test_list_plans(self, client, sample_wall_data, sample_plan_request):
        """Test listing plans for a wall."""
        # Create wall
        create_response = client.post("/walls", json=sample_wall_data)
        wall_id = create_response.json()["wall_id"]
        
        # Create multiple plans
        client.post(f"/walls/{wall_id}/plan", json=sample_plan_request)
        client.post(f"/walls/{wall_id}/plan", json={**sample_plan_request, "resolution": 0.2})
        
        # List plans
        response = client.get(f"/walls/{wall_id}/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) >= 2
    
    def test_get_plan_details(self, client, sample_wall_data, sample_plan_request):
        """Test getting detailed plan information."""
        # Create wall
        create_response = client.post("/walls", json=sample_wall_data)
        wall_id = create_response.json()["wall_id"]
        
        # Generate plan
        plan_response = client.post(f"/walls/{wall_id}/plan", json=sample_plan_request)
        plan_id = plan_response.json()["plan_id"]
        
        # Get plan details
        response = client.get(f"/walls/plans/{plan_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["plan_id"] == plan_id
        assert "paths" in data
        assert len(data["paths"]) > 0


class TestExecutionAPI:
    """Tests for Execution API endpoints."""
    
    def test_execute_path(self, client, sample_wall_data, sample_plan_request):
        """Test executing a path."""
        # Create wall and plan
        wall_response = client.post("/walls", json=sample_wall_data)
        wall_id = wall_response.json()["wall_id"]
        
        plan_response = client.post(f"/walls/{wall_id}/plan", json=sample_plan_request)
        path_id = plan_response.json()["best_path_id"]
        
        # Execute path
        response = client.post(f"/paths/{path_id}/execute")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SENT"
        assert "execution_id" in data
        assert data["path_id"] == path_id
    
    def test_execute_nonexistent_path(self, client):
        """Test executing a path that doesn't exist."""
        response = client.post("/paths/nonexistent-id/execute")
        assert response.status_code == 404
    
    def test_get_execution_status(self, client, sample_wall_data, sample_plan_request):
        """Test getting execution status."""
        # Create wall, plan, and execute
        wall_response = client.post("/walls", json=sample_wall_data)
        wall_id = wall_response.json()["wall_id"]
        
        plan_response = client.post(f"/walls/{wall_id}/plan", json=sample_plan_request)
        path_id = plan_response.json()["best_path_id"]
        
        exec_response = client.post(f"/paths/{path_id}/execute")
        execution_id = exec_response.json()["execution_id"]
        
        # Get status
        response = client.get(f"/paths/executions/{execution_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["execution_id"] == execution_id
        assert "status" in data
        assert "progress" in data
    
    def test_update_execution_status(self, client, sample_wall_data, sample_plan_request):
        """Test updating execution status."""
        # Create wall, plan, and execute
        wall_response = client.post("/walls", json=sample_wall_data)
        wall_id = wall_response.json()["wall_id"]
        
        plan_response = client.post(f"/walls/{wall_id}/plan", json=sample_plan_request)
        path_id = plan_response.json()["best_path_id"]
        
        exec_response = client.post(f"/paths/{path_id}/execute")
        execution_id = exec_response.json()["execution_id"]
        
        # Update status
        response = client.patch(
            f"/paths/executions/{execution_id}",
            params={"status": "RUNNING", "progress": 50.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "RUNNING"
        assert data["progress"] == 50.0


class TestTelemetryAPI:
    """Tests for Telemetry API endpoints."""
    
    def test_update_telemetry(self, client, sample_wall_data, sample_plan_request):
        """Test updating telemetry."""
        # Create wall, plan, and execute
        wall_response = client.post("/walls", json=sample_wall_data)
        wall_id = wall_response.json()["wall_id"]
        
        plan_response = client.post(f"/walls/{wall_id}/plan", json=sample_plan_request)
        path_id = plan_response.json()["best_path_id"]
        
        exec_response = client.post(f"/paths/{path_id}/execute")
        execution_id = exec_response.json()["execution_id"]
        
        # Update telemetry
        telemetry_data = {
            "execution_id": execution_id,
            "position": [2.5, 3.0],
            "progress": 45.5,
            "status": "RUNNING"
        }
        response = client.post("/telemetry/update", json=telemetry_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["execution_id"] == execution_id


class TestMonitoringAPI:
    """Tests for Monitoring API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_get_stats(self, client, sample_wall_data, sample_plan_request):
        """Test getting system statistics."""
        # Create some data
        wall_response = client.post("/walls", json=sample_wall_data)
        wall_id = wall_response.json()["wall_id"]
        
        client.post(f"/walls/{wall_id}/plan", json=sample_plan_request)
        
        # Get stats
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_plans" in data
        assert "total_paths" in data
        assert "total_executions" in data
        assert data["total_plans"] >= 1
