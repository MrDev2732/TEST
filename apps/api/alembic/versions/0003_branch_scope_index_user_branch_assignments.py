"""add branch-user composite index for scoped access queries

Revision ID: 0003_branch_scope_index_user_branch_assignments
Revises: 0002_integrity_user_branch_and_default_branch
Create Date: 2026-04-16
"""

from alembic import op

revision = "0003_branch_scope_index_user_branch_assignments"
down_revision = "0002_integrity_user_branch_and_default_branch"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    if is_sqlite:
        with op.batch_alter_table("user_branch_assignments") as batch_op:
            batch_op.create_index("ix_user_branch_assignments_branch_user", ["branch_id", "user_id"])
    else:
        op.create_index(
            "ix_user_branch_assignments_branch_user",
            "user_branch_assignments",
            ["branch_id", "user_id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    if is_sqlite:
        with op.batch_alter_table("user_branch_assignments") as batch_op:
            batch_op.drop_index("ix_user_branch_assignments_branch_user")
    else:
        op.drop_index("ix_user_branch_assignments_branch_user", table_name="user_branch_assignments")
