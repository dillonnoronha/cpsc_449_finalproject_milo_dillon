"""Reset and seed the database with sample users and tasks.

Run from the backend folder:  python -m scripts.seed
"""
from datetime import date

from app.core.security import hash_password
from app.db.database import Base, SessionLocal, engine
from app.models import Role, Task, TaskStatus, User

USERS = [
    {"name": "Admin User", "email": "admin@example.com", "password": "Admin123!", "role": Role.ADMIN},
    {"name": "Kamilo Ramirez", "email": "kamilo@example.com", "password": "Password123!", "role": Role.USER},
    {"name": "Dillon Noronha", "email": "dillon@example.com", "password": "Password123!", "role": Role.USER},
]

TASKS = {
    "kamilo@example.com": [
        ("Set up FastAPI project", "Create backend folder structure", date(2026, 10, 24), TaskStatus.COMPLETED),
        ("Implement JWT login", "POST /auth/login returns a token", date(2026, 11, 1), TaskStatus.IN_PROGRESS),
        ("Task CRUD endpoints", "GET/POST/PUT/DELETE /tasks", date(2026, 11, 11), TaskStatus.TODO),
    ],
    "dillon@example.com": [
        ("Integrate Nager.Date API", "Holiday lookups for due dates", date(2026, 10, 25), TaskStatus.COMPLETED),
        ("Build React login page", "Connect to /auth/login", date(2026, 11, 26), TaskStatus.TODO),
        ("Admin dashboard", "Protected page listing users", date(2026, 12, 24), TaskStatus.TODO),
    ],
}


def seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        users = {}
        for u in USERS:
            user = User(name=u["name"], email=u["email"], password_hash=hash_password(u["password"]), role=u["role"])
            db.add(user)
            users[u["email"]] = user

        for email, tasks in TASKS.items():
            for title, description, due_date, status in tasks:
                db.add(Task(owner=users[email], title=title, description=description, due_date=due_date, status=status))

        db.commit()
        print(f"Seeded {len(USERS)} users and {sum(len(t) for t in TASKS.values())} tasks.")


if __name__ == "__main__":
    seed()
