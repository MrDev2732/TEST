from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.models import User, Role
from app.repositories.access_scope_repository import AccessScopeRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
access_scope_repo = AccessScopeRepository()


class CurrentUser:
    def __init__(self, user: User, role: Role):
        self.user = user
        self.role = role


class AccessScope:
    def __init__(self, tenant_id: int | None, branch_ids: list[int] | None):
        self.tenant_id = tenant_id
        self.branch_ids = branch_ids


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = db.query(User).filter(User.id == int(sub)).first()
    if not user:
        raise credentials_exception
    role = db.query(Role).filter(Role.id == user.role_id).first()
    return CurrentUser(user=user, role=role)


def get_access_scope(current: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)) -> AccessScope:
    if current.role.name == "platform_admin":
        return AccessScope(tenant_id=None, branch_ids=None)
    if current.role.name == "tenant_admin":
        return AccessScope(tenant_id=current.user.tenant_id, branch_ids=None)
    if current.role.name in {"branch_admin", "seller"}:
        branch_ids = access_scope_repo.get_assigned_branch_ids(db, current.user.id)
        return AccessScope(tenant_id=current.user.tenant_id, branch_ids=branch_ids)
    return AccessScope(tenant_id=current.user.tenant_id, branch_ids=[])


def require_roles(*allowed: str):
    def _guard(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current.role.name not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current

    return _guard
