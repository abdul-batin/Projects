"""Planner service for coordinating path planning operations."""
import logging
from shapely.geometry import Polygon
from sqlalchemy.orm import Session
import sys
import os
import numpy as np

logger = logging.getLogger(__name__)

# Add parent directory to path to import algorithm modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from algorithm import planner as planner_module
from algorithm.grid_construction import Grid as GridBuilder
from db.repositories import PlanRepository, PathRepository, GridRepository


class PlannerService:
    """Service for planning robot coverage paths."""

    def __init__(self, db: Session):
        self.db = db

    async def run_plan(self, wall, obstacles, resolution):
        """
        Run path planning for a wall with obstacles.
        
        Args:
            wall: Wall data with id and geometry
            obstacles: List of obstacle data with geometry
            resolution: Grid resolution
            
        Returns:
            Tuple of (plan_id, candidates) where candidates is list of path info
        """
        # Create plan record
        logger.info(f"PlannerService: Starting plan for wall {wall['id']} with resolution {resolution}")
        plan_repo = PlanRepository(self.db)
        plan_record = plan_repo.create_plan(wall["id"], resolution)
        
        try:
            # Check for cached grid
            grid_repo = GridRepository(self.db)
            logger.debug(f"PlannerService: Checking grid cache for wall {wall['id']}")
            cached_grid = grid_repo.get_or_create_grid(wall["id"], resolution)
            
            if cached_grid and cached_grid.grid_data:
                # Use cached grid
                logger.info(f"PlannerService: Using cached grid for wall {wall['id']}")
                grid = np.array(cached_grid.grid_data, dtype=np.uint8)
            else:
                # Build new grid
                logger.info(f"PlannerService: Building new grid for wall {wall['id']}")
                wall_poly = Polygon(wall["geometry"])
                obs_polys = [Polygon(o["geometry"]) for o in obstacles]
                grid_builder = GridBuilder()
                grid = grid_builder.build_grid(wall_poly, obs_polys, resolution)
                logger.info(f"PlannerService: Grid built with shape {grid.shape}")
                
                # Cache the grid
                grid_repo.get_or_create_grid(wall["id"], resolution, grid)
                logger.debug(f"PlannerService: Grid cached")
            
            # Run planning algorithm
            logger.info(f"PlannerService: Running planning algorithms")
            result = planner_module.plan(grid)
            logger.info(f"PlannerService: Planning complete with {len(result['candidates'])} candidates")
            
            # Store paths in database
            path_repo = PathRepository(self.db)
            candidates = []
            best_path = None
            
            for candidate in result["candidates"]:
                path = path_repo.create_path(
                    plan_id=plan_record.id,
                    strategy=candidate["strategy"],
                    path_data=candidate["path"],
                    coverage=candidate["metrics"]["coverage"],
                    path_length=candidate["metrics"]["path_length"]
                )
                
                candidates.append({
                    "path_id": path.id,
                    "strategy": path.strategy,
                    "coverage": path.coverage,
                    "path_length": path.path_length
                })
                
                if best_path is None or path.coverage > best_path.coverage:
                    best_path = path
            
            # Update plan with best path
            plan_repo.update_plan_status(plan_record.id, "COMPLETED", best_path.id if best_path else None)
            logger.info(f"PlannerService: Plan {plan_record.id} completed successfully. Best path: {best_path.id if best_path else None}")
            
            return plan_record.id, candidates
            
        except Exception as e:
            # Mark plan as failed
            logger.error(f"PlannerService: Plan {plan_record.id} failed with error: {e}", exc_info=True)
            plan_repo.update_plan_status(plan_record.id, "FAILED")
            raise e

