from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import AccessScope, CurrentUser, get_access_scope, require_roles
from app.db.session import get_db
from app.models.models import Branch
from app.repositories.repository import CRUDRepository
from app.schemas.branch import BranchCreate, BranchRead, BranchUpdate
from app.services.policy_service import ensure_branch_access
from app.services.branch_service import create_branch as create_branch_tx, patch_branch as patch_branch_tx

router = APIRouter(prefix="/branches", tags=["branches"])
repo = CRUDRepository(Branch)


@router.get("", response_model=list[BranchRead])
def list_branches(
    current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin", "seller")),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    if current.role.name == "platform_admin":
        return repo.list(db, limit=limit, offset=offset)
    if current.role.name in {"branch_admin", "seller"}:
        return repo.list(db, [Branch.id.in_(scope.branch_ids or [])], limit=limit, offset=offset)
    return repo.list(db, [Branch.tenant_id == scope.tenant_id], limit=limit, offset=offset)


@router.post("", response_model=BranchRead)
def create_branch(payload: BranchCreate, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")), db: Session = Depends(get_db)):
    if current.role.name == "tenant_admin" and payload.tenant_id != current.user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden tenant")
    return create_branch_tx(db, payload.model_dump())


@router.get("/{branch_id}", response_model=BranchRead)
def get_branch(
    branch_id: int,
    current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin", "seller")),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
):
    entity = repo.get(db, branch_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    ensure_branch_access(current, scope, entity)
    return entity


@router.patch("/{branch_id}", response_model=BranchRead)
def patch_branch(
    branch_id: int,
    payload: BranchUpdate,
    current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin")),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
):
    entity = repo.get(db, branch_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    ensure_branch_access(current, scope, entity)
    return patch_branch_tx(db, entity, payload.model_dump(exclude_none=True))
