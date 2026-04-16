from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.core.security import hash_password
from app.db.session import Base
from app.main import app
from app.models.models import Role, Tenant, User

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_security.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add_all(
        [
            Role(id=1, name="seller", description="seller"),
            Role(id=2, name="branch_admin", description="branch admin"),
            Role(id=3, name="tenant_admin", description="tenant admin"),
            Role(id=4, name="platform_admin", description="platform admin"),
        ]
    )
    tenant = Tenant(name="Tenant Test", slug="tenant-test", status="active")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    tenant_admin = User(
        email="tenant-admin@test.com",
        full_name="Tenant Admin",
        status="active",
        tenant_id=tenant.id,
        role_id=3,
        default_branch_id=None,
        password_hash=hash_password("Pass1234!"),
    )
    seller = User(
        email="seller@test.com",
        full_name="Seller",
        status="active",
        tenant_id=tenant.id,
        role_id=1,
        default_branch_id=None,
        password_hash=hash_password("Pass1234!"),
    )
    db.add_all([tenant_admin, seller])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def _tenant_admin_token() -> str:
    login_response = client.post(
        "/auth/login",
        json={"email": "tenant-admin@test.com", "password": "Pass1234!"},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def test_tenant_admin_cannot_assign_platform_admin_role_on_create() -> None:
    token = _tenant_admin_token()

    response = client.post(
        "/users",
        json={
            "tenant_id": 1,
            "email": "new-admin@test.com",
            "full_name": "Attempted Platform Admin",
            "status": "active",
            "role_id": 4,
            "password": "Pass1234!",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


def test_tenant_admin_cannot_assign_platform_admin_role_on_patch() -> None:
    token = _tenant_admin_token()

    response = client.patch(
        "/users/2",
        json={"role_id": 4},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


def test_tenant_admin_create_ignores_null_tenant_and_scopes_to_own_tenant() -> None:
    token = _tenant_admin_token()

    response = client.post(
        "/users",
        json={
            "tenant_id": None,
            "email": "null-tenant@test.com",
            "full_name": "Null Tenant",
            "status": "active",
            "role_id": 1,
            "password": "Pass1234!",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # tenant_admin is force-scoped to their own tenant; request succeeds with server-side tenant override.
    assert response.status_code == 200
    assert response.json()["tenant_id"] == 1


def test_tenant_admin_cannot_assign_null_tenant_on_patch() -> None:
    token = _tenant_admin_token()

    response = client.patch(
        "/users/2",
        json={"tenant_id": None},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"
