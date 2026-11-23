"""Run from backend/: python scripts/seed.py. Updates only records with stable seed keys."""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import Task, User

PREFIX = "cpsc449:v1:"
USERS = [
    ("alex", "Alex Morgan", "alex.morgan@example.com", "user"),
    ("jordan", "Jordan Lee", "jordan.lee@example.com", "user"),
    ("taylor", "Taylor Brooks", "taylor.brooks@example.com", "admin"),
]
# Fixed UTC dates keep repeated runs reproducible. Four tasks belong to each user.
TASKS = [
    ("backend-checkpoint", "alex", "Complete backend checkpoint", "Document the working backend and database connection.", "in_progress", 2),
    ("postgres-schema", "alex", "Review PostgreSQL schema", "Check user foreign keys and nullable legacy task fields.", "completed", 1),
    ("api-tests", "alex", "Test API endpoints", "Exercise create/list requests and validation in Swagger UI.", "todo", 3),
    ("persistence", "alex", "Verify task persistence", "Restart the backend and confirm saved tasks remain available.", "todo", 4),
    ("dashboard", "jordan", "Implement frontend dashboard", "Build a task list and task creation form for the client.", "in_progress", 5),
    ("external-apis", "jordan", "Integrate external APIs", "Plan the holiday integration and document sample responses.", "todo", 7),
    ("client-validation", "jordan", "Review client validation", "Confirm task form errors explain required title fields.", "completed", 2),
    ("client-connect", "jordan", "Connect dashboard to backend", "Display tasks returned by the internal API.", "todo", 8),
    ("final-demo", "taylor", "Prepare final project demonstration", "Outline a walkthrough using synthetic development data.", "todo", 12),
    ("admin-plan", "taylor", "Plan administrative interface", "Sketch the future admin user listing without implementing authentication.", "in_progress", 9),
    ("screenshots", "taylor", "Capture checkpoint screenshots", "Collect database rows and successful API responses without secrets.", "completed", 3),
    ("team-review", "taylor", "Review team progress", "Compare completed work against the semester project milestones.", "todo", 10),
]


def seed():
    with SessionLocal.begin() as session:
        # Serialize concurrent runs of this script within PostgreSQL.
        session.execute(text("SELECT pg_advisory_xact_lock(4492026)"))
        owners = {}
        for key, name, email, role in USERS:
            seed_key = PREFIX + "user:" + key
            user = session.scalar(select(User).where(User.seed_key == seed_key))
            collision = session.scalar(select(User).where(User.email == email))
            if collision is not None and (user is None or collision.id != user.id):
                raise ValueError("Sample email belongs to an unrelated user; no seed changes were committed.")
            if user is None:
                user = User(seed_key=seed_key)
                session.add(user)
            elif user.password_hash is not None:
                raise ValueError("A sample user has login credentials; refusing to overwrite this record.")
            user.name, user.email, user.role = name, email, role
            user.password_hash = None
            owners[key] = user
        session.flush()
        for key, owner, title, description, status, day in TASKS:
            seed_key = PREFIX + "task:" + key
            task = session.scalar(select(Task).where(Task.seed_key == seed_key))
            if task is None:
                task = Task(seed_key=seed_key)
                session.add(task)
            task.title, task.description, task.status = title, description, status
            task.due_date = datetime(2026, 11, day, 17, tzinfo=timezone.utc)
            task.user = owners[owner]
    print("Seed committed: 3 sample users and 12 sample tasks (existing seed records updated).")


if __name__ == "__main__":
    try:
        seed()
    except (SQLAlchemyError, ValueError):
        print("Seed failed; transaction rolled back. Check migrations, database access, and sample email/credential conflicts.", file=sys.stderr)
        sys.exit(1)
