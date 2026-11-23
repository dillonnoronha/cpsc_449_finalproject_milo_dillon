"""Add users, optional task ownership/due dates, and stable development seed keys."""
from alembic import op
import sqlalchemy as sa

revision = "0002_users_and_task_details"
down_revision = "0001_task_baseline"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), server_default="user", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("seed_key", sa.String(100), nullable=True),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("seed_key", name="uq_users_seed_key"),
    )
    op.add_column("tasks", sa.Column("user_id", sa.Integer(), nullable=True))
    op.add_column("tasks", sa.Column("due_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("seed_key", sa.String(100), nullable=True))
    op.create_foreign_key("fk_tasks_user_id_users", "tasks", "users", ["user_id"], ["id"])
    op.create_unique_constraint("uq_tasks_seed_key", "tasks", ["seed_key"])


def downgrade():
    raise RuntimeError("Destructive downgrades are disabled; preserve users and tasks.")
