"""Unit tests for repository layer."""
import pytest
from db.repositories import (
    WallRepository,
    ObstacleRepository,
    PlanRepository,
    PathRepository,
    ExecutionRepository,
    GridRepository
)
from db.models import Wall, Obstacle, Plan, Path, Execution


class TestWallRepository:
    """Tests for WallRepository."""
    
    def test_create_wall(self, test_db):
        """Test creating a wall through repository."""
        repo = WallRepository(test_db)
        wall = repo.create_wall(
            name="Test Wall",
            geometry=[[0, 0], [5, 0], [5, 5], [0, 5]]
        )
        
        assert wall.id is not None
        assert wall.name == "Test Wall"
        assert len(wall.geometry) == 4
    
    def test_get_wall(self, test_db):
        """Test retrieving a wall."""
        repo = WallRepository(test_db)
        wall = repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        retrieved = repo.get_wall(wall.id)
        assert retrieved is not None
        assert retrieved.id == wall.id
        assert retrieved.name == "Test Wall"
    
    def test_get_all_walls(self, test_db):
        """Test getting all walls."""
        repo = WallRepository(test_db)
        repo.create_wall("Wall 1", [[0, 0], [5, 0], [5, 5], [0, 5]])
        repo.create_wall("Wall 2", [[0, 0], [10, 0], [10, 10], [0, 10]])
        
        walls = repo.get_all_walls()
        assert len(walls) == 2
    
    def test_delete_wall(self, test_db):
        """Test deleting a wall."""
        repo = WallRepository(test_db)
        wall = repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        success = repo.delete_wall(wall.id)
        assert success is True
        
        retrieved = repo.get_wall(wall.id)
        assert retrieved is None


class TestObstacleRepository:
    """Tests for ObstacleRepository."""
    
    def test_create_obstacle(self, test_db):
        """Test creating an obstacle."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        obstacle_repo = ObstacleRepository(test_db)
        obstacle = obstacle_repo.create_obstacle(
            wall_id=wall.id,
            obstacle_type="window",
            geometry=[[1, 1], [2, 1], [2, 2], [1, 2]]
        )
        
        assert obstacle.id is not None
        assert obstacle.type == "window"
        assert obstacle.wall_id == wall.id
    
    def test_get_obstacles_by_wall(self, test_db):
        """Test getting obstacles for a wall."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        obstacle_repo = ObstacleRepository(test_db)
        obstacle_repo.create_obstacle(wall.id, "window", [[1, 1], [2, 1], [2, 2], [1, 2]])
        obstacle_repo.create_obstacle(wall.id, "door", [[3, 3], [4, 3], [4, 4], [3, 4]])
        
        obstacles = obstacle_repo.get_obstacles_by_wall(wall.id)
        assert len(obstacles) == 2
    
    def test_delete_obstacle(self, test_db):
        """Test deleting an obstacle."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        obstacle_repo = ObstacleRepository(test_db)
        obstacle = obstacle_repo.create_obstacle(wall.id, "window", [[1, 1], [2, 1], [2, 2], [1, 2]])
        
        success = obstacle_repo.delete_obstacle(obstacle.id)
        assert success is True


class TestPlanRepository:
    """Tests for PlanRepository."""
    
    def test_create_plan(self, test_db):
        """Test creating a plan."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        plan_repo = PlanRepository(test_db)
        plan = plan_repo.create_plan(wall.id, 0.1)
        
        assert plan.id is not None
        assert plan.resolution == 0.1
        assert plan.status == "PENDING"
    
    def test_update_plan_status(self, test_db):
        """Test updating plan status."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        plan_repo = PlanRepository(test_db)
        plan = plan_repo.create_plan(wall.id, 0.1)
        
        updated = plan_repo.update_plan_status(plan.id, "COMPLETED", "path-123")
        assert updated.status == "COMPLETED"
        assert updated.best_path_id == "path-123"
    
    def test_get_plans_by_wall(self, test_db):
        """Test getting plans for a wall."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        plan_repo = PlanRepository(test_db)
        plan_repo.create_plan(wall.id, 0.1)
        plan_repo.create_plan(wall.id, 0.2)
        
        plans = plan_repo.get_plans_by_wall(wall.id)
        assert len(plans) == 2


class TestPathRepository:
    """Tests for PathRepository."""
    
    def test_create_path(self, test_db):
        """Test creating a path."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        plan_repo = PlanRepository(test_db)
        plan = plan_repo.create_plan(wall.id, 0.1)
        
        path_repo = PathRepository(test_db)
        path = path_repo.create_path(
            plan_id=plan.id,
            strategy="horizontal",
            path_data=[[0, 0], [1, 0], [2, 0]],
            coverage=0.95,
            path_length=100
        )
        
        assert path.id is not None
        assert path.strategy == "horizontal"
        assert path.coverage == 0.95
    
    def test_get_paths_by_plan(self, test_db):
        """Test getting paths for a plan."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        plan_repo = PlanRepository(test_db)
        plan = plan_repo.create_plan(wall.id, 0.1)
        
        path_repo = PathRepository(test_db)
        path_repo.create_path(plan.id, "horizontal", [[0, 0]], 0.95, 100)
        path_repo.create_path(plan.id, "vertical", [[0, 0]], 0.93, 110)
        
        paths = path_repo.get_paths_by_plan(plan.id)
        assert len(paths) == 2
    
    def test_update_execution_status(self, test_db):
        """Test updating path execution status."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        plan_repo = PlanRepository(test_db)
        plan = plan_repo.create_plan(wall.id, 0.1)
        
        path_repo = PathRepository(test_db)
        path = path_repo.create_path(plan.id, "horizontal", [[0, 0]], 0.95, 100)
        
        updated = path_repo.update_execution_status(path.id, "RUNNING")
        assert updated.execution_status == "RUNNING"


class TestExecutionRepository:
    """Tests for ExecutionRepository."""
    
    def test_create_execution(self, test_db):
        """Test creating an execution."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        plan_repo = PlanRepository(test_db)
        plan = plan_repo.create_plan(wall.id, 0.1)
        
        path_repo = PathRepository(test_db)
        path = path_repo.create_path(plan.id, "horizontal", [[0, 0]], 0.95, 100)
        
        exec_repo = ExecutionRepository(test_db)
        execution = exec_repo.create_execution(path.id)
        
        assert execution.id is not None
        assert execution.status == "SENT"
    
    def test_update_execution_status(self, test_db):
        """Test updating execution status."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        plan_repo = PlanRepository(test_db)
        plan = plan_repo.create_plan(wall.id, 0.1)
        
        path_repo = PathRepository(test_db)
        path = path_repo.create_path(plan.id, "horizontal", [[0, 0]], 0.95, 100)
        
        exec_repo = ExecutionRepository(test_db)
        execution = exec_repo.create_execution(path.id)
        
        updated = exec_repo.update_execution_status(
            execution.id, "RUNNING", progress=45.5
        )
        assert updated.status == "RUNNING"
        assert updated.progress == 45.5


class TestGridRepository:
    """Tests for GridRepository."""
    
    def test_get_or_create_grid(self, test_db):
        """Test grid caching."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        grid_repo = GridRepository(test_db)
        import numpy as np
        grid_data = np.array([[0, 1, 0], [1, 0, 1]], dtype=np.uint8)
        
        # Create grid
        grid = grid_repo.get_or_create_grid(wall.id, 0.1, grid_data)
        assert grid is not None
        assert grid.resolution == 0.1
        
        # Retrieve cached grid
        cached = grid_repo.get_or_create_grid(wall.id, 0.1)
        assert cached is not None
        assert cached.id == grid.id
    
    def test_invalidate_grid(self, test_db):
        """Test grid invalidation."""
        wall_repo = WallRepository(test_db)
        wall = wall_repo.create_wall("Test Wall", [[0, 0], [5, 0], [5, 5], [0, 5]])
        
        grid_repo = GridRepository(test_db)
        import numpy as np
        grid_data = np.array([[0, 1]], dtype=np.uint8)
        
        grid_repo.get_or_create_grid(wall.id, 0.1, grid_data)
        
        # Invalidate
        grid_repo.invalidate_grid(wall.id)
        
        # Should not find cached grid
        cached = grid_repo.get_or_create_grid(wall.id, 0.1)
        assert cached is None
