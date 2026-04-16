from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.login_protection import login_protection
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import MeResponse
from app.services.auth_service import login, me

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login_route(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    login_protection.evaluate_and_delay(client_ip, payload.email)
    try:
        token = login(db, payload.email, payload.password)
        login_protection.register_result(client_ip, payload.email, success=True)
    except HTTPException:
        login_protection.register_result(client_ip, payload.email, success=False)
        raise
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me_route(current=Depends(get_current_user), db: Session = Depends(get_db)):
    return me(db, current.user)


@router.get("/login/metrics")
def login_metrics():
    return login_protection.get_metrics()
