import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from repositories import PathRepository, ExecutionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/paths", tags=["execution"])


@router.post("/{path_id}/execute")
async def execute_path(path_id: str, db: Session = Depends(get_db)):
    """Execute a path on the robot."""
    logger.info(f"API: Executing path {path_id}")
    # Fetch path from DB
    path_repo = PathRepository(db)
    path = path_repo.get_path(path_id)
    if not path:
        logger.warning(f"API: Path {path_id} not found")
        raise HTTPException(status_code=404, detail="Path not found")
    
    # Create execution record
    execution_repo = ExecutionRepository(db)
    execution = execution_repo.create_execution(path_id)
    logger.info(f"API: Execution {execution.id} created for path {path_id}")
    
    # Update path status
    path_repo.update_execution_status(path_id, "RUNNING")
    
    # TODO: Publish to message broker for actual robot execution
    # For now, just mark as sent
    logger.info(f"API: Path {path_id} execution sent")
    
    return {
        "status": "SENT",
        "execution_id": execution.id,
        "path_id": path_id
    }


@router.get("/{path_id}/executions")
async def get_path_executions(path_id: str, db: Session = Depends(get_db)):
    """Get all executions for a path."""
    execution_repo = ExecutionRepository(db)
    executions = execution_repo.get_executions_by_path(path_id)
    return {
        "executions": [
            {
                "execution_id": e.id,
                "status": e.status,
                "progress": e.progress,
                "started_at": e.started_at,
                "completed_at": e.completed_at,
                "error_message": e.error_message
            }
            for e in executions
        ]
    }


@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str, db: Session = Depends(get_db)):
    """Get status of a specific execution."""
    execution_repo = ExecutionRepository(db)
    execution = execution_repo.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {
        "execution_id": execution.id,
        "path_id": execution.path_id,
        "status": execution.status,
        "progress": execution.progress,
        "started_at": execution.started_at,
        "completed_at": execution.completed_at,
        "error_message": execution.error_message
    }


@router.patch("/executions/{execution_id}")
async def update_execution_status(
    execution_id: str,
    status: str,
    progress: float = None,
    error_message: str = None,
    db: Session = Depends(get_db)
):
    """Update execution status (typically called by robot or monitoring service)."""
    execution_repo = ExecutionRepository(db)
    execution = execution_repo.update_execution_status(
        execution_id, status, progress, error_message
    )
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {
        "execution_id": execution.id,
        "status": execution.status,
        "progress": execution.progress
    }
