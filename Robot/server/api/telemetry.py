"""Telemetry API for robot status updates."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from repositories import ExecutionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class TelemetryUpdate(BaseModel):
    """Telemetry update from robot."""
    execution_id: str
    position: list  # [x, y] coordinates
    progress: float
    status: str


@router.post("/update")
async def update_telemetry(update: TelemetryUpdate, db: Session = Depends(get_db)):
    """Receive telemetry update from robot."""
    logger.info(f"API: Telemetry update for execution {update.execution_id}: progress={update.progress}%, status={update.status}")
    execution_repo = ExecutionRepository(db)
    execution = execution_repo.get_execution(update.execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Update execution status
    execution_repo.update_execution_status(
        update.execution_id,
        update.status,
        update.progress
    )
    
    return {
        "status": "received",
        "execution_id": update.execution_id,
        "progress": update.progress
    }


@router.get("/{execution_id}/current")
async def get_current_telemetry(execution_id: str, db: Session = Depends(get_db)):
    """Get current telemetry for an execution."""
    execution_repo = ExecutionRepository(db)
    execution = execution_repo.get_execution(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {
        "execution_id": execution.id,
        "status": execution.status,
        "progress": execution.progress,
        "started_at": execution.started_at
    }
