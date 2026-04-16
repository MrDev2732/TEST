from collections.abc import Mapping

from sqlalchemy.orm import Session

from app.models.models import Role


ALLOWED_ROLE_ASSIGNMENTS: Mapping[str, set[str]] = {
    "platform_admin": {"seller", "branch_admin", "tenant_admin", "platform_admin"},
    "tenant_admin": {"seller", "branch_admin", "tenant_admin"},
}


def validate_role_assignment(db: Session, actor_role: str, target_role_id: int) -> bool:
    allowed_roles = ALLOWED_ROLE_ASSIGNMENTS.get(actor_role)
    if not allowed_roles:
        return False
    target_role = db.query(Role).filter(Role.id == target_role_id).first()
    if target_role is None:
        return False
    return target_role.name in allowed_roles
