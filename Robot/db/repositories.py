"""Repository layer for database operations."""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from .models import Wall, Obstacle, Plan, Path, Execution, Grid
import numpy as np

logger = logging.getLogger(__name__)


class WallRepository:
    """Repository for Wall operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_wall(self, name: str, geometry: List[List[float]]) -> Wall:
        """Create a new wall."""
        logger.info(f"Creating wall: {name}")
        wall = Wall(name=name, geometry=geometry)
        self.db.add(wall)
        self.db.commit()
        self.db.refresh(wall)
        logger.info(f"Wall created with ID: {wall.id}")
        return wall
    
    def get_wall(self, wall_id: str) -> Optional[Wall]:
        """Get wall by ID."""
        return self.db.query(Wall).filter(Wall.id == wall_id).first()
    
    def get_all_walls(self) -> List[Wall]:
        """Get all walls."""
        return self.db.query(Wall).all()
    
    def delete_wall(self, wall_id: str) -> bool:
        """Delete a wall."""
        wall = self.get_wall(wall_id)
        if wall:
            self.db.delete(wall)
            self.db.commit()
            return True
        return False


class ObstacleRepository:
    """Repository for Obstacle operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_obstacle(self, wall_id: str, obstacle_type: str, geometry: List[List[float]]) -> Obstacle:
        """Create a new obstacle."""
        obstacle = Obstacle(wall_id=wall_id, type=obstacle_type, geometry=geometry)
        self.db.add(obstacle)
        self.db.commit()
        self.db.refresh(obstacle)
        return obstacle
    
    def get_obstacles_by_wall(self, wall_id: str) -> List[Obstacle]:
        """Get all obstacles for a wall."""
        return self.db.query(Obstacle).filter(Obstacle.wall_id == wall_id).all()
    
    def delete_obstacle(self, obstacle_id: str) -> bool:
        """Delete an obstacle."""
        obstacle = self.db.query(Obstacle).filter(Obstacle.id == obstacle_id).first()
        if obstacle:
            self.db.delete(obstacle)
            self.db.commit()
            return True
        return False


class PlanRepository:
    """Repository for Plan operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_plan(self, wall_id: str, resolution: float) -> Plan:
        """Create a new plan."""
        logger.info(f"Creating plan for wall {wall_id} with resolution {resolution}")
        plan = Plan(wall_id=wall_id, resolution=resolution, status="PENDING")
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        logger.info(f"Plan created with ID: {plan.id}")
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan by ID."""
        return self.db.query(Plan).filter(Plan.id == plan_id).first()
    
    def update_plan_status(self, plan_id: str, status: str, best_path_id: Optional[str] = None):
        """Update plan status."""
        plan = self.get_plan(plan_id)
        if plan:
            plan.status = status
            if best_path_id:
                plan.best_path_id = best_path_id
            self.db.commit()
            self.db.refresh(plan)
        return plan
    
    def get_plans_by_wall(self, wall_id: str) -> List[Plan]:
        """Get all plans for a wall."""
        return self.db.query(Plan).filter(Plan.wall_id == wall_id).all()


class PathRepository:
    """Repository for Path operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_path(self, plan_id: str, strategy: str, path_data: List, 
                   coverage: float, path_length: int) -> Path:
        """Create a new path."""
        path = Path(
            plan_id=plan_id,
            strategy=strategy,
            path_data=path_data,
            coverage=coverage,
            path_length=path_length
        )
        self.db.add(path)
        self.db.commit()
        self.db.refresh(path)
        return path
    
    def get_path(self, path_id: str) -> Optional[Path]:
        """Get path by ID."""
        return self.db.query(Path).filter(Path.id == path_id).first()
    
    def get_paths_by_plan(self, plan_id: str) -> List[Path]:
        """Get all paths for a plan."""
        return self.db.query(Path).filter(Path.plan_id == plan_id).all()
    
    def update_execution_status(self, path_id: str, status: str):
        """Update path execution status."""
        path = self.get_path(path_id)
        if path:
            path.execution_status = status
            self.db.commit()
            self.db.refresh(path)
        return path


class ExecutionRepository:
    """Repository for Execution operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_execution(self, path_id: str) -> Execution:
        """Create a new execution."""
        execution = Execution(path_id=path_id, status="SENT")
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[Execution]:
        """Get execution by ID."""
        return self.db.query(Execution).filter(Execution.id == execution_id).first()
    
    def update_execution_status(self, execution_id: str, status: str, 
                               progress: Optional[float] = None,
                               error_message: Optional[str] = None) -> Optional[Execution]:
        """Update execution status."""
        execution = self.get_execution(execution_id)
        if execution:
            execution.status = status
            if progress is not None:
                execution.progress = progress
            if error_message:
                execution.error_message = error_message
            self.db.commit()
            self.db.refresh(execution)
        return execution
    
    def get_executions_by_path(self, path_id: str) -> List[Execution]:
        """Get all executions for a path."""
        return self.db.query(Execution).filter(Execution.path_id == path_id).all()


class GridRepository:
    """Repository for Grid caching operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_grid(self, wall_id: str, resolution: float, 
                          grid_data: Optional[np.ndarray] = None) -> Optional[Grid]:
        """Get cached grid or create new one."""
        grid = self.db.query(Grid).filter(
            and_(Grid.wall_id == wall_id, Grid.resolution == resolution)
        ).first()
        
        if not grid and grid_data is not None:
            grid = Grid(
                wall_id=wall_id,
                resolution=resolution,
                grid_data=grid_data.tolist()
            )
            self.db.add(grid)
            self.db.commit()
            self.db.refresh(grid)
        
        return grid
    
    def invalidate_grid(self, wall_id: str):
        """Invalidate all cached grids for a wall."""
        self.db.query(Grid).filter(Grid.wall_id == wall_id).delete()
        self.db.commit()
