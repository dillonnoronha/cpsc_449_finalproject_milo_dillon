"""Recognize the original tasks table or create it on a fresh database."""
from alembic import op
import sqlalchemy as sa

revision = "0001_task_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("tasks"):
        columns = {column["name"]: column for column in inspector.get_columns("tasks")}
        expected = {"id", "title", "description", "status", "created_at"}
        if set(columns) != expected:
            raise RuntimeError("Existing tasks schema differs from the original foundation; review before migrating.")
        if inspector.get_pk_constraint("tasks")["constrained_columns"] != ["id"]:
            raise RuntimeError("Existing tasks primary key differs; review before migrating.")
        if not (
            isinstance(columns["id"]["type"], sa.Integer)
            and isinstance(columns["title"]["type"], sa.String)
            and columns["title"]["type"].length == 255
            and isinstance(columns["description"]["type"], sa.Text)
            and isinstance(columns["status"]["type"], sa.String)
            and columns["status"]["type"].length == 50
            and isinstance(columns["created_at"]["type"], sa.DateTime)
            and columns["created_at"]["type"].timezone
            and columns["description"]["nullable"]
            and all(not columns[name]["nullable"] for name in expected - {"description"})
        ):
            raise RuntimeError("Existing tasks column definitions differ; review before migrating.")
        return
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade():
    raise RuntimeError("Destructive downgrades are disabled; preserve existing task data.")
