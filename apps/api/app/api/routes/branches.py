from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import AccessScope, CurrentUser, get_access_scope, require_roles
from app.db.session import get_db
from app.models.models import Branch
from app.repositories.repository import AccessScopeRepository, CRUDRepository
from app.schemas.branch import BranchCreate, BranchRead, BranchUpdate

router = APIRouter(prefix="/branches", tags=["branches"])
repo = CRUDRepository(Branch)
access_repo = AccessScopeRepository()


@router.get("", response_model=list[BranchRead])
def list_branches(
    current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin", "branch_admin", "seller")),
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
):
    if current.role.name == "platform_admin":
        return repo.list(db)
    if current.role.name == "branch_admin":
        branch_ids = scope.branch_ids or []
        if not branch_ids:
            return []
        return repo.list(db, [Branch.id.in_(branch_ids)])
    return repo.list(db, [Branch.tenant_id == scope.tenant_id])


@router.post("", response_model=BranchRead)
def create_branch(payload: BranchCreate, current: CurrentUser = Depends(require_roles("platform_admin", "tenant_admin")), db: Session = Depends(get_db)):
    if current.role.name == "tenant_admin" and payload.tenant_id != current.user.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden tenant")
    return repo.create(db, payload.model_dump())


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

    if current.role.name == "branch_admin":
        if not access_repo.branch_in_scope(db, branch_id, scope.branch_ids or []):
            raise HTTPException(status_code=403, detail="Forbidden")
    elif current.role.name != "platform_admin" and entity.tenant_id != scope.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
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

    if current.role.name == "branch_admin":
        if not access_repo.branch_in_scope(db, branch_id, scope.branch_ids or []):
            raise HTTPException(status_code=403, detail="Forbidden")
    elif current.role.name != "platform_admin" and entity.tenant_id != scope.tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return repo.update(db, entity, payload.model_dump(exclude_none=True))
