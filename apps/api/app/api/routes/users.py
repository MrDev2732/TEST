from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import AccessScope, CurrentUser, get_access_scope, require_roles
from app.core.security import hash_password
from app.db.session import get_db
from app.models.models import User
from app.repositories.access_scope_repository import AccessScopeRepository
from app.repositories.repository import CRUDRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service
from app.services.authorization_service import validate_role_assignment
from app.services.user_service import validate_default_branch_tenant_consistency

router = APIRouter(prefix="/users", tags=["users"])
repo = CRUDRepository(User)
access_scope_repo = AccessScopeRepository()


@router.get("", response_model=list[UserRead])
def list_users(
    current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin")),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
):
    if current.role.name == "platform_admin":
        return repo.list(db)
    if current.role.name == "branch_admin":
        return access_scope_repo.list_users_in_branches(db, scope.branch_ids or [])
    return repo.list(db, [User.tenant_id == scope.tenant_id])


@router.post("", response_model=UserRead)
def create_user(payload: UserCreate, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")), db: Session = Depends(get_db)):
    if not validate_role_assignment(current.role.name, payload.role_id):
        raise HTTPException(status_code=403, detail="Forbidden")

    data = payload.model_dump(exclude={"password"})
    if current.role.name != "platform_admin" and payload.tenant_id is None:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current.role.name == "tenant_admin":
        data["tenant_id"] = current.user.tenant_id
    validate_default_branch_tenant_consistency(db, data.get("tenant_id"), data.get("default_branch_id"))
    data["password_hash"] = hash_password(payload.password)
    return user_service.create_user(db, data)


def _validate_user_scope(entity: User, current: CurrentUser, scope: AccessScope, db: Session) -> None:
    if current.role.name == "platform_admin":
        return
    if current.role.name == "branch_admin":
        if not access_scope_repo.user_in_branches(db, entity.id, scope.branch_ids or []):
            raise HTTPException(status_code=403, detail="Forbidden")
        return
    if entity.tenant_id != scope.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin")),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
):
    entity = repo.get(db, user_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    _validate_user_scope(entity, current, scope, db)
    return entity


@router.patch("/{user_id}", response_model=UserRead)
def patch_user(
    user_id: int,
    payload: UserUpdate,
    current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
):
    entity = repo.get(db, user_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    _validate_user_scope(entity, current, scope, db)
    data = payload.model_dump(exclude_none=True)
    if payload.role_id is not None and not validate_role_assignment(current.role.name, payload.role_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    if current.role.name != "platform_admin" and payload.tenant_id is None and "tenant_id" in payload.model_fields_set:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current.role.name == "tenant_admin":
        data.pop("tenant_id", None)
    target_tenant_id = data.get("tenant_id", entity.tenant_id)
    target_default_branch_id = data.get("default_branch_id", entity.default_branch_id)
    validate_default_branch_tenant_consistency(db, target_tenant_id, target_default_branch_id)
    return user_service.patch_user(db, entity, data)
