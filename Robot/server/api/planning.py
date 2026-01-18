import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import PlanRequest, PlanResponse, PlanCandidate
from services.planner_service import PlannerService
from database import get_db
from repositories import WallRepository, ObstacleRepository, PlanRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/walls", tags=["planning"])


@router.post("/{wall_id}/plan", response_model=PlanResponse)
async def plan_wall(wall_id: str, req: PlanRequest, db: Session = Depends(get_db)):
    """Generate a coverage plan for a wall."""
    logger.info(f"API: Planning wall {wall_id} with resolution {req.resolution}")
    # Fetch wall from DB
    wall_repo = WallRepository(db)
    wall = wall_repo.get_wall(wall_id)
    if not wall:
        logger.warning(f"API: Wall {wall_id} not found")
        raise HTTPException(status_code=404, detail="Wall not found")
    
    # Fetch obstacles from DB
    obstacle_repo = ObstacleRepository(db)
    obstacles = obstacle_repo.get_obstacles_by_wall(wall_id)
    
    # Convert to format expected by planner
    wall_data = {"id": wall.id, "geometry": wall.geometry}
    obstacles_data = [{"geometry": o.geometry} for o in obstacles]
    
    # Run planning
    planner = PlannerService(db=db)
    plan_id, candidates = await planner.run_plan(wall_data, obstacles_data, req.resolution)
    
    # Convert candidates to response format
    candidate_responses = []
    best_path_id = None
    for i, c in enumerate(candidates):
        candidate_responses.append(
            PlanCandidate(
                path_id=c["path_id"],
                coverage=c["coverage"],
                path_length=c["path_length"]
            )
        )
        if i == 0:  # First candidate is best
            best_path_id = c["path_id"]
    
    return PlanResponse(
        plan_id=plan_id,
        best_path_id=best_path_id,
        candidates=candidate_responses
    )


@router.get("/{wall_id}/plans")
async def list_plans(wall_id: str, db: Session = Depends(get_db)):
    """List all plans for a wall."""
    plan_repo = PlanRepository(db)
    plans = plan_repo.get_plans_by_wall(wall_id)
    return {
        "plans": [
            {
                "plan_id": p.id,
                "resolution": p.resolution,
                "status": p.status,
                "best_path_id": p.best_path_id,
                "created_at": p.created_at
            }
            for p in plans
        ]
    }


@router.get("/plans/{plan_id}")
async def get_plan_details(plan_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a plan."""
    plan_repo = PlanRepository(db)
    plan = plan_repo.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return {
        "plan_id": plan.id,
        "wall_id": plan.wall_id,
        "resolution": plan.resolution,
        "status": plan.status,
        "best_path_id": plan.best_path_id,
        "created_at": plan.created_at,
        "paths": [
            {
                "path_id": p.id,
                "strategy": p.strategy,
                "coverage": p.coverage,
                "path_length": p.path_length,
                "execution_status": p.execution_status
            }
            for p in plan.paths
        ]
    }
