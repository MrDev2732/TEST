from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, require_roles
from app.db.session import get_db
from app.models.models import Branch
from app.repositories.repository import CRUDRepository
from app.schemas.branch import BranchCreate, BranchRead, BranchUpdate
from app.services.branch_service import create_branch as create_branch_tx, patch_branch as patch_branch_tx

router = APIRouter(prefix="/branches", tags=["branches"])
repo = CRUDRepository(Branch)


@router.get("", response_model=list[BranchRead])
def list_branches(current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin", "seller")), db: Session = Depends(get_db)):
    if current.role.name == "platform_admin":
        return repo.list(db)
    return repo.list(db, [Branch.tenant_id == current.user.tenant_id])


@router.post("", response_model=BranchRead)
def create_branch(payload: BranchCreate, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")), db: Session = Depends(get_db)):
    if current.role.name == "tenant_admin" and payload.tenant_id != current.user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden tenant")
    return create_branch_tx(db, payload.model_dump())


@router.get("/{branch_id}", response_model=BranchRead)
def get_branch(branch_id: int, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin", "seller")), db: Session = Depends(get_db)):
    entity = repo.get(db, branch_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    if current.role.name != "platform_admin" and entity.tenant_id != current.user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return entity


@router.patch("/{branch_id}", response_model=BranchRead)
def patch_branch(branch_id: int, payload: BranchUpdate, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin")), db: Session = Depends(get_db)):
    entity = repo.get(db, branch_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    if current.role.name != "platform_admin" and entity.tenant_id != current.user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return patch_branch_tx(db, entity, payload.model_dump(exclude_none=True))
