from datetime import datetime
from pydantic import BaseModel
from app.schemas.common import ORMModel


class BranchCreate(BaseModel):
    tenant_id: int
    name: str
    code: str
    status: str = "active"
    address: str | None = None


class BranchUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    status: str | None = None
    address: str | None = None


class BranchRead(ORMModel):
    id: int
    tenant_id: int
    name: str
    code: str
    status: str
    address: str | None
    created_at: datetime
    updated_at: datetime
