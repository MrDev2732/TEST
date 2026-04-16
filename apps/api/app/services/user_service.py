from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError, InvalidForeignKey
from app.models.models import Branch, User
from app.repositories.repository import CRUDRepository
from app.services.persistence_service import map_integrity_error

repo = CRUDRepository(User)


def validate_default_branch_tenant_consistency(db: Session, tenant_id: int | None, default_branch_id: int | None) -> None:
    if default_branch_id is None:
        return

    if tenant_id is None:
        raise DomainError("default_branch_id requiere tenant_id")

    branch = db.query(Branch).filter(Branch.id == default_branch_id).first()
    if not branch:
        raise InvalidForeignKey("default_branch_id no existe")

    if branch.tenant_id != tenant_id:
        raise InvalidForeignKey("default_branch_id no pertenece al tenant del usuario")


def create_user(db: Session, payload: dict[str, Any]) -> User:
    entity = repo.create(db, payload)
    try:
        db.commit()
        db.refresh(entity)
    except IntegrityError as error:
        db.rollback()
        raise map_integrity_error(error) from error
    return entity


def patch_user(db: Session, entity: User, payload: dict[str, Any]) -> User:
    entity = repo.update(db, entity, payload)
    try:
        db.commit()
        db.refresh(entity)
    except IntegrityError as error:
        db.rollback()
        raise map_integrity_error(error) from error
    return entity
