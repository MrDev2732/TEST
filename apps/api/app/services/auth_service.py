from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import verify_password, create_access_token
from app.models.models import User, Role


def login(db: Session, email: str, password: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    return create_access_token(str(user.id))


def me(db: Session, user: User) -> dict:
    role = db.query(Role).filter(Role.id == user.role_id).first()
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": role.name,
        "tenant_id": user.tenant_id,
        "default_branch_id": user.default_branch_id,
    }
