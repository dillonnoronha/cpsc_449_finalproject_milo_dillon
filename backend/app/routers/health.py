from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Task, User

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    """Confirms the API is running and the PostgreSQL connection works."""
    try:
        db.execute(text("SELECT 1"))
        users = db.scalar(select(func.count()).select_from(User))
        tasks = db.scalar(select(func.count()).select_from(Task))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok", "database": "connected", "users": users, "tasks": tasks}
