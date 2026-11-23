"""Provision two dedicated local demo accounts using environment credentials."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.models import User
from app.security import hash_password


ACCOUNTS = (
    ("user", "Regular Demo", "demo.user@example.com", "DEMO_USER_PASSWORD"),
    ("admin", "Admin Demo", "demo.admin@example.com", "DEMO_ADMIN_PASSWORD"),
)


def provision() -> None:
    passwords = [os.environ.get(variable, "") for _, _, _, variable in ACCOUNTS]
    if any(not 12 <= len(password) <= 1024 for password in passwords):
        raise ValueError("Set both demo passwords to 12–1024 characters.")
    if passwords[0] == passwords[1]:
        raise ValueError("Use distinct demo passwords.")

    hashes = [hash_password(password) for password in passwords]
    with SessionLocal.begin() as db:
        for (role, name, email, _), password_hash in zip(ACCOUNTS, hashes, strict=True):
            seed_key = f"cpsc449:auth-demo:v1:{role}"
            statement = insert(User).values(
                name=name, email=email, role=role, password_hash=password_hash, seed_key=seed_key
            )
            statement = statement.on_conflict_do_update(
                index_elements=[User.email],
                set_={"password_hash": statement.excluded.password_hash},
                where=(User.seed_key == seed_key) & (User.role == role),
            ).returning(User.id)
            if db.scalar(statement) is None:
                raise ValueError("A demo email belongs to a different account. No changes committed.")


if __name__ == "__main__":
    try:
        if "--confirm-local-demo" not in sys.argv[1:]:
            raise ValueError("Point DATABASE_URL to a disposable local database and pass --confirm-local-demo.")
        provision()
    except ValueError as error:
        sys.exit(str(error))
    except SQLAlchemyError:
        sys.exit("Demo setup failed. Check database access and migrations. No changes committed.")
    print("Local regular and admin demo accounts are ready.")
