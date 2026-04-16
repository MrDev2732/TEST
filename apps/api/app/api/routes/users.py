from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import AccessScope, CurrentUser, get_access_scope, require_roles
from app.core.security import hash_password
from app.db.session import get_db
from app.models.models import User
from app.repositories.repository import AccessScopeRepository, CRUDRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service
from app.services.user_service import validate_default_branch_tenant_consistency

router = APIRouter(prefix="/users", tags=["users"])
repo = CRUDRepository(User)
access_repo = AccessScopeRepository()


@router.get("", response_model=list[UserRead])
def list_users(
    current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin")),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
):
    if current.role.name == "platform_admin":
        return repo.list(db)
    if current.role.name == "branch_admin":
        return access_repo.list_users_for_branch_scope(db, scope.branch_ids or [])
    return repo.list(db, [User.tenant_id == scope.tenant_id])


@router.post("", response_model=UserRead)
def create_user(payload: UserCreate, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")), db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"password"})
    if current.role.name == "tenant_admin":
        data["tenant_id"] = current.user.tenant_id
    validate_default_branch_tenant_consistency(db, data.get("tenant_id"), data.get("default_branch_id"))
    data["password_hash"] = hash_password(payload.password)
    return user_service.create_user(db, data)


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

    if current.role.name == "branch_admin":
        if not access_repo.user_in_branch_scope(db, user_id, scope.branch_ids or []):
            raise HTTPException(status_code=403, detail="Forbidden")
    elif current.role.name != "platform_admin" and entity.tenant_id != scope.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return entity


@router.patch("/{user_id}", response_model=UserRead)
def patch_user(
    user_id: int,
    payload: UserUpdate,
    current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin")),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
):
    entity = repo.get(db, user_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")

    if current.role.name == "branch_admin":
        if not access_repo.user_in_branch_scope(db, user_id, scope.branch_ids or []):
            raise HTTPException(status_code=403, detail="Forbidden")
    elif current.role.name != "platform_admin" and entity.tenant_id != scope.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = payload.model_dump(exclude_none=True)
    if current.role.name == "tenant_admin":
        data.pop("tenant_id", None)
    if current.role.name == "branch_admin":
        data.pop("tenant_id", None)
        data.pop("role_id", None)
    target_tenant_id = data.get("tenant_id", entity.tenant_id)
    target_default_branch_id = data.get("default_branch_id", entity.default_branch_id)
    validate_default_branch_tenant_consistency(db, target_tenant_id, target_default_branch_id)
    return user_service.patch_user(db, entity, data)