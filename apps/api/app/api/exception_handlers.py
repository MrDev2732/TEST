from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import DomainError, DuplicateEmail, DuplicateResource, InvalidForeignKey
from app.services.persistence_service import map_integrity_error


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DuplicateEmail)
    async def handle_duplicate_email(_: Request, exc: DuplicateEmail):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(DuplicateResource)
    async def handle_duplicate_resource(_: Request, exc: DuplicateResource):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(InvalidForeignKey)
    async def handle_invalid_foreign_key(_: Request, exc: InvalidForeignKey):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, exc: DomainError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(_: Request, exc: IntegrityError):
        mapped = map_integrity_error(exc)
        if isinstance(mapped, DuplicateEmail | DuplicateResource):
            status_code = 409
        elif isinstance(mapped, InvalidForeignKey):
            status_code = 422
        else:
            status_code = 422
        return JSONResponse(status_code=status_code, content={"detail": str(mapped)})
