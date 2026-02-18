from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, DbReviewJob

router = APIRouter()


class JobOut(BaseModel):
    id: str
    document_id: str
    status: str
    provider: Optional[str] = None
    model: Optional[str] = None
    trigger: str = "manual"
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


@router.get("/", response_model=List[JobOut])
async def list_jobs(limit: int = 20, db: Session = Depends(get_db)):
    """List recent review jobs"""
    jobs = db.query(DbReviewJob).order_by(DbReviewJob.created_at.desc()).limit(limit).all()
    return [
        JobOut(
            id=j.id,
            document_id=j.document_id,
            status=j.status,
            provider=j.provider,
            model=j.model,
            trigger=j.trigger,
            error_message=j.error_message,
            created_at=j.created_at.isoformat(),
            completed_at=j.completed_at.isoformat() if j.completed_at else None,
        )
        for j in jobs
    ]
