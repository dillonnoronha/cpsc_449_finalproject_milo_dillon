from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import Task
from .schemas import TaskCreate, TaskResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()


app = FastAPI(title="Task Management API", lifespan=lifespan)
DbSession = Annotated[Session, Depends(get_db)]


def database_error() -> HTTPException:
    return HTTPException(status_code=503, detail="Database unavailable. Please try again later.")


@app.get("/")
def root():
    return {"message": "Task Management API is running"}


@app.get("/health/db")
def database_health(db: DbSession):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise database_error() from None
    return {"status": "ok", "database": "connected"}


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: DbSession):
    task = Task(**payload.model_dump())
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Task data violates a database constraint; check user_id.") from None
    except SQLAlchemyError:
        db.rollback()
        raise database_error() from None
    return task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: DbSession):
    try:
        return db.scalars(select(Task).order_by(Task.id)).all()
    except SQLAlchemyError:
        raise database_error() from None
