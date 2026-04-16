from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, require_roles
from app.core.security import hash_password
from app.db.session import get_db
from app.models.models import User
from app.repositories.repository import CRUDRepository
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])
repo = CRUDRepository(User)


@router.get("", response_model=list[UserRead])
def list_users(current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin")), db: Session = Depends(get_db)):
    if current.role.name == "platform_admin":
        return repo.list(db)
    return repo.list(db, [User.tenant_id == current.user.tenant_id])


@router.post("", response_model=UserRead)
def create_user(payload: UserCreate, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")), db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"password"})
    if current.role.name == "tenant_admin":
        data["tenant_id"] = current.user.tenant_id
    data["password_hash"] = hash_password(payload.password)
    return repo.create(db, data)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin")), db: Session = Depends(get_db)):
    entity = repo.get(db, user_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    if current.role.name != "platform_admin" and entity.tenant_id != current.user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return entity


@router.patch("/{user_id}", response_model=UserRead)
def patch_user(user_id: int, payload: UserUpdate, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")), db: Session = Depends(get_db)):
    entity = repo.get(db, user_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    if current.role.name != "platform_admin" and entity.tenant_id != current.user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    data = payload.model_dump(exclude_none=True)
    if current.role.name == "tenant_admin":
        data.pop("tenant_id", None)
    return repo.update(db, entity, data)
