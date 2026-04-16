"""add user branch assignment constraints

Revision ID: 0002_user_branch_assignment_constraints
Revises: 0001_sprint1_base
Create Date: 2026-04-16
"""

from alembic import op

revision = "0002_user_branch_assignment_constraints"
down_revision = "0001_sprint1_base"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_user_branch_assignments_user_id",
        "user_branch_assignments",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_branch_assignments_branch_id",
        "user_branch_assignments",
        ["branch_id"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_user_branch_assignment",
        "user_branch_assignments",
        ["user_id", "branch_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_branch_assignment", "user_branch_assignments", type_="unique")
    op.drop_index("ix_user_branch_assignments_branch_id", table_name="user_branch_assignments")
    op.drop_index("ix_user_branch_assignments_user_id", table_name="user_branch_assignments")
