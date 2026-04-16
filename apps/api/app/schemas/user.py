from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.schemas.common import ORMModel


class UserCreate(BaseModel):
    tenant_id: int | None = None
    email: EmailStr
    full_name: str
    status: str = "active"
    role_id: int
    default_branch_id: int | None = None
    password: str


class UserUpdate(BaseModel):
    tenant_id: int | None = None
    full_name: str | None = None
    status: str | None = None
    role_id: int | None = None
    default_branch_id: int | None = None


class UserRead(ORMModel):
    id: int
    auth_provider_user_id: str | None
    tenant_id: int | None
    email: EmailStr
    full_name: str
    status: str
    role_id: int
    default_branch_id: int | None
    created_at: datetime
    updated_at: datetime


class MeResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    tenant_id: int | None
    default_branch_id: int | None
