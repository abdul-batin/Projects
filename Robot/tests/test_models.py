"""Unit tests for database models."""
import pytest
from db.models import Wall, Obstacle, Plan, Path, Execution, Grid


class TestWallModel:
    """Tests for Wall model."""
    
    def test_create_wall(self, test_db):
        """Test creating a wall."""
        wall = Wall(
            name="Test Wall",
            geometry=[[0, 0], [5, 0], [5, 5], [0, 5]]
        )
        test_db.add(wall)
        test_db.commit()
        test_db.refresh(wall)
        
        assert wall.id is not None
        assert wall.name == "Test Wall"
        assert len(wall.geometry) == 4
        assert wall.created_at is not None
    
    def test_wall_relationships(self, test_db):
        """Test wall relationships with obstacles and plans."""
        wall = Wall(name="Test Wall", geometry=[[0, 0], [5, 0], [5, 5], [0, 5]])
        test_db.add(wall)
        test_db.commit()
        
        # Add obstacle
        obstacle = Obstacle(
            wall_id=wall.id,
            type="window",
            geometry=[[1, 1], [2, 1], [2, 2], [1, 2]]
        )
        test_db.add(obstacle)
        test_db.commit()
        
        test_db.refresh(wall)
        assert len(wall.obstacles) == 1
        assert wall.obstacles[0].type == "window"


class TestObstacleModel:
    """Tests for Obstacle model."""
    
    def test_create_obstacle(self, test_db):
        """Test creating an obstacle."""
        wall = Wall(name="Test Wall", geometry=[[0, 0], [5, 0], [5, 5], [0, 5]])
        test_db.add(wall)
        test_db.commit()
        
        obstacle = Obstacle(
            wall_id=wall.id,
            type="door",
            geometry=[[2, 0], [3, 0], [3, 2], [2, 2]]
        )
        test_db.add(obstacle)
        test_db.commit()
        test_db.refresh(obstacle)
        
        assert obstacle.id is not None
        assert obstacle.type == "door"
        assert obstacle.wall_id == wall.id
    
    def test_obstacle_cascade_delete(self, test_db):
        """Test that deleting a wall cascades to obstacles."""
        wall = Wall(name="Test Wall", geometry=[[0, 0], [5, 0], [5, 5], [0, 5]])
        test_db.add(wall)
        test_db.commit()
        
        obstacle = Obstacle(
            wall_id=wall.id,
            type="window",
            geometry=[[1, 1], [2, 1], [2, 2], [1, 2]]
        )
        test_db.add(obstacle)
        test_db.commit()
        
        obstacle_id = obstacle.id
        
        # Delete wall
        test_db.delete(wall)
        test_db.commit()
        
        # Obstacle should be deleted
        assert test_db.query(Obstacle).filter(Obstacle.id == obstacle_id).first() is None


class TestPlanModel:
    """Tests for Plan model."""
    
    def test_create_plan(self, test_db):
        """Test creating a plan."""
        wall = Wall(name="Test Wall", geometry=[[0, 0], [5, 0], [5, 5], [0, 5]])
        test_db.add(wall)
        test_db.commit()
        
        plan = Plan(
            wall_id=wall.id,
            resolution=0.1,
            status="PENDING"
        )
        test_db.add(plan)
        test_db.commit()
        test_db.refresh(plan)
        
        assert plan.id is not None
        assert plan.resolution == 0.1
        assert plan.status == "PENDING"
    
    def test_plan_status_update(self, test_db):
        """Test updating plan status."""
        wall = Wall(name="Test Wall", geometry=[[0, 0], [5, 0], [5, 5], [0, 5]])
        test_db.add(wall)
        test_db.commit()
        
        plan = Plan(wall_id=wall.id, resolution=0.1, status="PENDING")
        test_db.add(plan)
        test_db.commit()
        
        plan.status = "COMPLETED"
        test_db.commit()
        test_db.refresh(plan)
        
        assert plan.status == "COMPLETED"


class TestPathModel:
    """Tests for Path model."""
    
    def test_create_path(self, test_db):
        """Test creating a path."""
        wall = Wall(name="Test Wall", geometry=[[0, 0], [5, 0], [5, 5], [0, 5]])
        test_db.add(wall)
        test_db.commit()
        
        plan = Plan(wall_id=wall.id, resolution=0.1)
        test_db.add(plan)
        test_db.commit()
        
        path = Path(
            plan_id=plan.id,
            strategy="horizontal",
            path_data=[[0, 0], [1, 0], [2, 0]],
            coverage=0.95,
            path_length=100
        )
        test_db.add(path)
        test_db.commit()
        test_db.refresh(path)
        
        assert path.id is not None
        assert path.strategy == "horizontal"
        assert path.coverage == 0.95
        assert path.path_length == 100


class TestExecutionModel:
    """Tests for Execution model."""
    
    def test_create_execution(self, test_db):
        """Test creating an execution."""
        wall = Wall(name="Test Wall", geometry=[[0, 0], [5, 0], [5, 5], [0, 5]])
        test_db.add(wall)
        test_db.commit()
        
        plan = Plan(wall_id=wall.id, resolution=0.1)
        test_db.add(plan)
        test_db.commit()
        
        path = Path(
            plan_id=plan.id,
            strategy="horizontal",
            path_data=[[0, 0], [1, 0]],
            coverage=0.95,
            path_length=100
        )
        test_db.add(path)
        test_db.commit()
        
        execution = Execution(
            path_id=path.id,
            status="SENT",
            progress=0.0
        )
        test_db.add(execution)
        test_db.commit()
        test_db.refresh(execution)
        
        assert execution.id is not None
        assert execution.status == "SENT"
        assert execution.progress == 0.0
    
    def test_execution_progress_update(self, test_db):
        """Test updating execution progress."""
        wall = Wall(name="Test Wall", geometry=[[0, 0], [5, 0], [5, 5], [0, 5]])
        test_db.add(wall)
        test_db.commit()
        
        plan = Plan(wall_id=wall.id, resolution=0.1)
        test_db.add(plan)
        test_db.commit()
        
        path = Path(
            plan_id=plan.id,
            strategy="horizontal",
            path_data=[[0, 0]],
            coverage=0.95,
            path_length=100
        )
        test_db.add(path)
        test_db.commit()
        
        execution = Execution(path_id=path.id, status="RUNNING", progress=0.0)
        test_db.add(execution)
        test_db.commit()
        
        execution.progress = 50.5
        execution.status = "RUNNING"
        test_db.commit()
        test_db.refresh(execution)
        
        assert execution.progress == 50.5
        assert execution.status == "RUNNING"


class TestGridModel:
    """Tests for Grid model."""
    
    def test_create_grid(self, test_db):
        """Test creating a grid cache entry."""
        wall = Wall(name="Test Wall", geometry=[[0, 0], [5, 0], [5, 5], [0, 5]])
        test_db.add(wall)
        test_db.commit()
        
        grid = Grid(
            wall_id=wall.id,
            resolution=0.1,
            grid_data=[[0, 0, 1], [0, 1, 0], [1, 0, 0]]
        )
        test_db.add(grid)
        test_db.commit()
        test_db.refresh(grid)
        
        assert grid.id is not None
        assert grid.resolution == 0.1
        assert len(grid.grid_data) == 3
