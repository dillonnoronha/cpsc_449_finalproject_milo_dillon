from fastapi import FastAPI

from app.db.database import Base, engine
from app.routers import health, holidays

# Creates any missing tables on startup (a migration tool can replace this later)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CPSC 449 Task Manager API", version="0.1.0")

app.include_router(health.router)
app.include_router(holidays.router)


@app.get("/")
def root():
    return {"message": "Task Manager API is running. See /docs for all endpoints."}
