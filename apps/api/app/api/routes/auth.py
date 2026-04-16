from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import MeResponse
from app.services.auth_service import login, me

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, db: Session = Depends(get_db)):
    token = login(db, payload.email, payload.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me_route(current=Depends(get_current_user), db: Session = Depends(get_db)):
    return me(db, current.user)
