import asyncio

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db

READINESS_DB_TIMEOUT_SECONDS = 0.5

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/ready")
async def ready(db: Session = Depends(get_db)):
    try:
        await asyncio.wait_for(asyncio.to_thread(db.execute, text("SELECT 1")), timeout=READINESS_DB_TIMEOUT_SECONDS)
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database readiness check timed out",
        ) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database connection is not ready",
        ) from exc

    return {"status": "ready"}
