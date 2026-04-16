"""
Script de saneamiento previo a la migración de integridad.

Uso:
    python scripts_sanitize_integrity.py
"""

from sqlalchemy import text

from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        duplicated_assignments = db.execute(
            text(
                """
                SELECT COUNT(*)::int AS count
                FROM (
                    SELECT user_id, branch_id
                    FROM user_branch_assignments
                    GROUP BY user_id, branch_id
                    HAVING COUNT(*) > 1
                ) AS duplicates;
                """
            )
        ).scalar_one()

        inconsistent_default_branch = db.execute(
            text(
                """
                SELECT COUNT(*)::int AS count
                FROM users AS u
                JOIN branches AS b ON b.id = u.default_branch_id
                WHERE u.default_branch_id IS NOT NULL
                  AND (u.tenant_id IS NULL OR u.tenant_id <> b.tenant_id);
                """
            )
        ).scalar_one()

        print(f"Duplicados en user_branch_assignments: {duplicated_assignments}")
        print(f"default_branch_id inconsistentes: {inconsistent_default_branch}")

        if duplicated_assignments > 0:
            db.execute(
                text(
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
            )

        if inconsistent_default_branch > 0:
            db.execute(
                text(
                    """
                    UPDATE users AS u
                    SET default_branch_id = NULL
                    FROM branches AS b
                    WHERE u.default_branch_id = b.id
                      AND u.default_branch_id IS NOT NULL
                      AND (u.tenant_id IS NULL OR u.tenant_id <> b.tenant_id);
                    """
                )
            )

        db.commit()
        print("Saneamiento finalizado.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
