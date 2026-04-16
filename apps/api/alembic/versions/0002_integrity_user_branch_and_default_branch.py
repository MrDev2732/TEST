"""add integrity constraints for user-branch relations

Revision ID: 0002_integrity_user_branch_and_default_branch
Revises: 0001_sprint1_base
Create Date: 2026-04-16
"""

from alembic import op

revision = "0002_integrity_user_branch_and_default_branch"
down_revision = "0001_sprint1_base"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

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
        UPDATE users
        SET default_branch_id = NULL
        WHERE default_branch_id IS NOT NULL
          AND (
            tenant_id IS NULL OR tenant_id <> (
                SELECT tenant_id
                FROM branches
                WHERE branches.id = users.default_branch_id
            )
          );
        """
    )

    if is_sqlite:
        with op.batch_alter_table("user_branch_assignments") as batch_op:
            batch_op.create_unique_constraint(
                "uq_user_branch_assignments_user_branch",
                ["user_id", "branch_id"],
            )
            batch_op.create_index("ix_user_branch_assignments_user_id", ["user_id"])
            batch_op.create_index("ix_user_branch_assignments_branch_id", ["branch_id"])

        with op.batch_alter_table("branches") as batch_op:
            batch_op.create_unique_constraint("uq_branch_tenant_id_id", ["tenant_id", "id"])

        with op.batch_alter_table("users") as batch_op:
            batch_op.create_check_constraint(
                "ck_users_default_branch_requires_tenant",
                "default_branch_id IS NULL OR tenant_id IS NOT NULL",
            )
            batch_op.create_foreign_key(
                "fk_users_default_branch_tenant_consistency",
                "branches",
                ["tenant_id", "default_branch_id"],
                ["tenant_id", "id"],
            )
    else:
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
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    if is_sqlite:
        with op.batch_alter_table("users") as batch_op:
            batch_op.drop_constraint("fk_users_default_branch_tenant_consistency", type_="foreignkey")
            batch_op.drop_constraint("ck_users_default_branch_requires_tenant", type_="check")

        with op.batch_alter_table("branches") as batch_op:
            batch_op.drop_constraint("uq_branch_tenant_id_id", type_="unique")

        with op.batch_alter_table("user_branch_assignments") as batch_op:
            batch_op.drop_index("ix_user_branch_assignments_branch_id")
            batch_op.drop_index("ix_user_branch_assignments_user_id")
            batch_op.drop_constraint("uq_user_branch_assignments_user_branch", type_="unique")
    else:
        op.drop_constraint("fk_users_default_branch_tenant_consistency", "users", type_="foreignkey")
        op.drop_constraint("ck_users_default_branch_requires_tenant", "users", type_="check")
        op.drop_constraint("uq_branch_tenant_id_id", "branches", type_="unique")

        op.drop_index("ix_user_branch_assignments_branch_id", table_name="user_branch_assignments")
        op.drop_index("ix_user_branch_assignments_user_id", table_name="user_branch_assignments")
        op.drop_constraint("uq_user_branch_assignments_user_branch", "user_branch_assignments", type_="unique")
