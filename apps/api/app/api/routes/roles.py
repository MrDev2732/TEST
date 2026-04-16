from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Role
from app.schemas.role import RoleRead

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleRead])
def list_roles(_: object = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Role).order_by(Role.id).all()
