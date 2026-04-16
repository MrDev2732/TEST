from fastapi import HTTPException

from app.api.deps import AccessScope, CurrentUser
from app.models.models import Branch, Tenant, User
from app.repositories.access_scope_repository import AccessScopeRepository


def ensure_tenant_access(current: CurrentUser, tenant: Tenant) -> None:
    if current.role.name == "platform_admin":
        return
    if current.role.name == "tenant_admin" and current.user.tenant_id == tenant.id:
        return
    raise HTTPException(status_code=403, detail="Forbidden tenant")


def ensure_branch_access(current: CurrentUser, scope: AccessScope, branch: Branch) -> None:
    if current.role.name == "platform_admin":
        return
    if current.role.name in {"branch_admin", "seller"}:
        if branch.id in (scope.branch_ids or []):
            return
        raise HTTPException(status_code=403, detail="Forbidden")
    if current.role.name == "tenant_admin" and branch.tenant_id == scope.tenant_id:
        return
    raise HTTPException(status_code=403, detail="Forbidden")


def ensure_user_access(
    entity: User,
    current: CurrentUser,
    scope: AccessScope,
    access_scope_repo: AccessScopeRepository,
    db,
) -> None:
    if current.role.name == "platform_admin":
        return
    if current.role.name == "branch_admin":
        if access_scope_repo.user_in_branches(db, entity.id, scope.branch_ids or []):
            return
        raise HTTPException(status_code=403, detail="Forbidden")
    if entity.tenant_id == scope.tenant_id:
        return
    raise HTTPException(status_code=403, detail="Forbidden")
