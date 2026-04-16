from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import Branch


def validate_default_branch_tenant_consistency(
    db: Session, tenant_id: int | None, default_branch_id: int | None
) -> None:
    if default_branch_id is None:
        return

    if tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail="default_branch_id requiere tenant_id",
        )

    branch = db.query(Branch).filter(Branch.id == default_branch_id).first()
    if not branch:
        raise HTTPException(status_code=400, detail="default_branch_id no existe")

    if branch.tenant_id != tenant_id:
        raise HTTPException(
            status_code=400,
            detail="default_branch_id no pertenece al tenant del usuario",
        )
