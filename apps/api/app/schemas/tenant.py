from datetime import datetime
from pydantic import BaseModel
from app.schemas.common import ORMModel


class TenantCreate(BaseModel):
    name: str
    slug: str
    status: str = "active"


class TenantUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    status: str | None = None


class TenantRead(ORMModel):
    id: int
    name: str
    slug: str
    status: str
    created_at: datetime
    updated_at: datetime
