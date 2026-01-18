import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from db import models as db_models

logger = logging.getLogger(__name__)

router = APIRouter(tags=["monitoring"])


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics."""
    # Get counts from database
    all_plans = db.query(db_models.Plan).all()
    all_paths = db.query(db_models.Path).all()
    all_executions = db.query(db_models.Execution).all()
    
    return {
        "total_plans": len(all_plans),
        "total_paths": len(all_paths),
        "total_executions": len(all_executions),
        "active_executions": len([e for e in all_executions if e.status == "RUNNING"])
    }
