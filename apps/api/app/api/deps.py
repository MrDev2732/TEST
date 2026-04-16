from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.models import Role, User
from app.repositories.repository import AccessScopeRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class CurrentUser:
    def __init__(self, user: User, role: Role):
        self.user = user
        self.role = role


@dataclass
class AccessScope:
    tenant_id: int | None
    branch_ids: list[int] | None


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

    if current.role.name == "branch_admin":
        branch_ids = AccessScopeRepository().list_branch_ids_for_user(db, current.user.id)
        if not branch_ids and current.user.default_branch_id:
            branch_ids = [current.user.default_branch_id]
        return AccessScope(tenant_id=current.user.tenant_id, branch_ids=branch_ids)

    return AccessScope(tenant_id=current.user.tenant_id, branch_ids=None)


def require_roles(*allowed: str):
    def _guard(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current.role.name not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current

    return _guard
