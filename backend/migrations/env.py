from alembic import context

from app.database import Base, engine
from app import models  # Register tables with metadata.

if context.is_offline_mode():
    raise RuntimeError("These migrations require an online PostgreSQL connection to inspect the existing schema.")

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()
