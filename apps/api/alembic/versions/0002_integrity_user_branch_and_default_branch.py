"""add integrity constraints for user-branch relations

Revision ID: 0002_integrity_user_branch_and_default_branch
Revises: 0001_sprint1_base
Create Date: 2026-04-16
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_integrity_user_branch_and_default_branch"
down_revision = "0001_sprint1_base"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        WITH duplicated_assignments AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY user_id, branch_id
                    ORDER BY id
                ) AS duplicate_rank
            FROM user_branch_assignments
        )
        DELETE FROM user_branch_assignments
        WHERE id IN (
            SELECT id
            FROM duplicated_assignments
            WHERE duplicate_rank > 1
        );
        """
    )

    op.execute(
        """
        UPDATE users AS u
        SET default_branch_id = NULL
        FROM branches AS b
        WHERE u.default_branch_id = b.id
          AND u.default_branch_id IS NOT NULL
          AND (u.tenant_id IS NULL OR u.tenant_id <> b.tenant_id);
        """
    )

    op.create_unique_constraint(
        "uq_user_branch_assignments_user_branch",
        "user_branch_assignments",
        ["user_id", "branch_id"],
    )
    op.create_index(
        "ix_user_branch_assignments_user_id",
        "user_branch_assignments",
        ["user_id"],
    )
    op.create_index(
        "ix_user_branch_assignments_branch_id",
        "user_branch_assignments",
        ["branch_id"],
    )

    op.create_unique_constraint(
        "uq_branch_tenant_id_id",
        "branches",
        ["tenant_id", "id"],
    )

    op.create_check_constraint(
        "ck_users_default_branch_requires_tenant",
        "users",
        "default_branch_id IS NULL OR tenant_id IS NOT NULL",
    )
    op.create_foreign_key(
        "fk_users_default_branch_tenant_consistency",
        "users",
        "branches",
        ["tenant_id", "default_branch_id"],
        ["tenant_id", "id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_default_branch_tenant_consistency", "users", type_="foreignkey")
    op.drop_constraint("ck_users_default_branch_requires_tenant", "users", type_="check")
    op.drop_constraint("uq_branch_tenant_id_id", "branches", type_="unique")

    op.drop_index("ix_user_branch_assignments_branch_id", table_name="user_branch_assignments")
    op.drop_index("ix_user_branch_assignments_user_id", table_name="user_branch_assignments")
    op.drop_constraint("uq_user_branch_assignments_user_branch", "user_branch_assignments", type_="unique")
