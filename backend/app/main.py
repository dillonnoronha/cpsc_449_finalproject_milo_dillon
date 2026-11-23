from contextlib import asynccontextmanager
from typing import Annotated

from anyio import from_thread
from fastapi import FastAPI, HTTPException, Path, Request, Response, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .auth import CurrentUser, login, router as auth_router
from .config import frontend_origins
from .database import DbSession, database_error, engine
from .models import Task
from .schemas import TaskCreate, TaskResponse
from .task_events import publish_task_change, router as task_events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()


app = FastAPI(title="Task Management API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins(),
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth_router)
app.include_router(task_events_router)
TaskId = Annotated[int, Path(ge=1, le=2**31 - 1)]


@app.exception_handler(RequestValidationError)
async def validate_request(request: Request, exc: RequestValidationError):
    if request.scope.get("endpoint") is login:
        return JSONResponse(status_code=422, content={"detail": "Invalid login request."})
    return await request_validation_exception_handler(request, exc)


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


def commit_task(db: DbSession) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Task data violates a database constraint.") from None
    except SQLAlchemyError:
        db.rollback()
        raise database_error() from None


def owned_task(task_id: int, user_id: int, db: DbSession, *, for_write: bool = False) -> Task:
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    if for_write:
        query = query.with_for_update()
    try:
        task = db.scalar(query)
    except SQLAlchemyError:
        raise database_error() from None
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: DbSession, user: CurrentUser):
    task = Task(**payload.model_dump(), user_id=user.id)
    db.add(task)
    try:
        db.flush()
        result = TaskResponse.model_validate(task)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Task data violates a database constraint.") from None
    except SQLAlchemyError:
        db.rollback()
        raise database_error() from None
    owner_id = user.id
    commit_task(db)
    from_thread.run_sync(publish_task_change, owner_id)
    return result


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: DbSession, user: CurrentUser):
    try:
        return db.scalars(select(Task).where(Task.user_id == user.id).order_by(Task.id)).all()
    except SQLAlchemyError:
        raise database_error() from None


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: TaskId, db: DbSession, user: CurrentUser):
    return owned_task(task_id, user.id, db)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: TaskId, payload: TaskCreate, db: DbSession, user: CurrentUser):
    task = owned_task(task_id, user.id, db, for_write=True)
    task.title = payload.title
    task.description = payload.description
    task.status = payload.status
    task.due_date = payload.due_date
    result = TaskResponse.model_validate(task)
    owner_id = user.id
    commit_task(db)
    from_thread.run_sync(publish_task_change, owner_id)
    return result


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: TaskId, db: DbSession, user: CurrentUser):
    task = owned_task(task_id, user.id, db, for_write=True)
    db.delete(task)
    owner_id = user.id
    commit_task(db)
    from_thread.run_sync(publish_task_change, owner_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
