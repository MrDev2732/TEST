from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import Tenant
from app.repositories.repository import CRUDRepository
from app.services.persistence_service import map_integrity_error

repo = CRUDRepository(Tenant)


def create_tenant(db: Session, payload: dict):
    entity = repo.create(db, payload)
    try:
        db.commit()
        db.refresh(entity)
    except IntegrityError as error:
        db.rollback()
        raise map_integrity_error(error) from error
    return entity


def patch_tenant(db: Session, entity: Tenant, payload: dict):
    entity = repo.update(db, entity, payload)
    try:
        db.commit()
        db.refresh(entity)
    except IntegrityError as error:
        db.rollback()
        raise map_integrity_error(error) from error
    return entity
