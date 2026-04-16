from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, require_roles
from app.db.session import get_db
from app.models.models import Tenant
from app.repositories.repository import CRUDRepository
from app.schemas.tenant import TenantCreate, TenantRead, TenantUpdate
from app.services.tenant_service import create_tenant as create_tenant_tx, patch_tenant as patch_tenant_tx

router = APIRouter(prefix="/tenants", tags=["tenants"])
repo = CRUDRepository(Tenant)


@router.get("", response_model=list[TenantRead])
def list_tenants(current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")), db: Session = Depends(get_db)):
    if current.role.name == "tenant_admin":
        return repo.list(db, [Tenant.id == current.user.tenant_id])
    return repo.list(db)


@router.post("", response_model=TenantRead)
def create_tenant(payload: TenantCreate, _: CurrentUser = Depends(require_roles("platform_admin")), db: Session = Depends(get_db)):
    return create_tenant_tx(db, payload.model_dump())


@router.get("/{tenant_id}", response_model=TenantRead)
def get_tenant(tenant_id: int, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")), db: Session = Depends(get_db)):
    if current.role.name == "tenant_admin" and current.user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden tenant")
    entity = repo.get(db, tenant_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    return entity


@router.patch("/{tenant_id}", response_model=TenantRead)
def patch_tenant(tenant_id: int, payload: TenantUpdate, _: CurrentUser = Depends(require_roles("platform_admin")), db: Session = Depends(get_db)):
    entity = repo.get(db, tenant_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    return patch_tenant_tx(db, entity, payload.model_dump(exclude_none=True))
