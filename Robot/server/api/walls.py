import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import CreateWallRequest, CreateObstacleRequest, WallResponse
from database import get_db
from repositories import WallRepository, ObstacleRepository, GridRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/walls", tags=["walls"])


@router.post("", response_model=WallResponse)
async def create_wall(req: CreateWallRequest, db: Session = Depends(get_db)):
    """Create a new wall."""
    logger.info(f"API: Creating wall '{req.name}'")
    try:
        wall_repo = WallRepository(db)
        wall = wall_repo.create_wall(name=req.name, geometry=req.geometry.coordinates)
        logger.info(f"API: Wall created successfully with ID {wall.id}")
        return {"wall_id": wall.id}
    except Exception as e:
        logger.error(f"API: Error creating wall: {e}")
        raise


@router.get("/{wall_id}")
async def get_wall(wall_id: str, db: Session = Depends(get_db)):
    """Get wall details by ID."""
    wall_repo = WallRepository(db)
    wall = wall_repo.get_wall(wall_id)
    if not wall:
        raise HTTPException(status_code=404, detail="Wall not found")
    return {
        "wall_id": wall.id,
        "name": wall.name,
        "geometry": wall.geometry,
        "created_at": wall.created_at
    }


@router.get("")
async def list_walls(db: Session = Depends(get_db)):
    """List all walls."""
    wall_repo = WallRepository(db)
    walls = wall_repo.get_all_walls()
    return {
        "walls": [
            {
                "wall_id": w.id,
                "name": w.name,
                "geometry": w.geometry,
                "created_at": w.created_at
            }
            for w in walls
        ]
    }


@router.delete("/{wall_id}")
async def delete_wall(wall_id: str, db: Session = Depends(get_db)):
    """Delete a wall and all associated data."""
    wall_repo = WallRepository(db)
    success = wall_repo.delete_wall(wall_id)
    if not success:
        raise HTTPException(status_code=404, detail="Wall not found")
    return {"status": "deleted"}


@router.post("/{wall_id}/obstacles")
async def create_obstacle(wall_id: str, req: CreateObstacleRequest, db: Session = Depends(get_db)):
    """Create an obstacle for a wall."""
    # Verify wall exists
    wall_repo = WallRepository(db)
    wall = wall_repo.get_wall(wall_id)
    if not wall:
        raise HTTPException(status_code=404, detail="Wall not found")
    
    # Create obstacle
    obstacle_repo = ObstacleRepository(db)
    obstacle = obstacle_repo.create_obstacle(
        wall_id=wall_id,
        obstacle_type=req.type,
        geometry=req.geometry.coordinates
    )
    
    # Invalidate grid cache
    grid_repo = GridRepository(db)
    grid_repo.invalidate_grid(wall_id)
    
    return {"status": "created", "obstacle_id": obstacle.id}


@router.get("/{wall_id}/obstacles")
async def get_obstacles(wall_id: str, db: Session = Depends(get_db)):
    """Get all obstacles for a wall."""
    obstacle_repo = ObstacleRepository(db)
    obstacles = obstacle_repo.get_obstacles_by_wall(wall_id)
    return {
        "obstacles": [
            {
                "obstacle_id": o.id,
                "type": o.type,
                "geometry": o.geometry,
                "created_at": o.created_at
            }
            for o in obstacles
        ]
    }
