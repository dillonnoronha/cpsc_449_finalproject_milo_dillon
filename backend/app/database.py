import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("Set DATABASE_URL in the environment or backend/.env.")
try:
    parsed_url = make_url(database_url)
except Exception:
    raise RuntimeError("DATABASE_URL must be a valid PostgreSQL URL.") from None
if parsed_url.drivername != "postgresql+psycopg":
    raise RuntimeError("DATABASE_URL must use the postgresql+psycopg driver.")

engine = create_engine(parsed_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as session:
        yield session
