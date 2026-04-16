from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password
from app.db.session import Base
from app.main import app
from app.models.models import Branch, Role, Tenant, User


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        roles = [
            Role(id=1, name="seller", description="Seller"),
            Role(id=2, name="branch_admin", description="Branch Admin"),
            Role(id=3, name="tenant_admin", description="Tenant Admin"),
            Role(id=4, name="platform_admin", description="Platform Admin"),
        ]
        db.add_all(roles)

        tenant_1 = Tenant(id=1, name="Tenant One", slug="tenant-one", status="active")
        tenant_2 = Tenant(id=2, name="Tenant Two", slug="tenant-two", status="active")
        db.add_all([tenant_1, tenant_2])

        branch_1 = Branch(id=1, tenant_id=1, name="T1 Main", code="T1M", status="active")
        branch_2 = Branch(id=2, tenant_id=2, name="T2 Main", code="T2M", status="active")
        db.add_all([branch_1, branch_2])

        users = [
            User(
                id=1,
                email="seller@t1.example.com",
                full_name="Seller T1",
                status="active",
                tenant_id=1,
                role_id=1,
                default_branch_id=1,
                password_hash=hash_password("Pass1234!"),
            ),
            User(
                id=2,
                email="branch@t1.example.com",
                full_name="Branch Admin T1",
                status="active",
                tenant_id=1,
                role_id=2,
                default_branch_id=1,
                password_hash=hash_password("Pass1234!"),
            ),
            User(
                id=3,
                email="tenant@t1.example.com",
                full_name="Tenant Admin T1",
                status="active",
                tenant_id=1,
                role_id=3,
                default_branch_id=1,
                password_hash=hash_password("Pass1234!"),
            ),
            User(
                id=4,
                email="platform@test.com",
                full_name="Platform Admin",
                status="active",
                tenant_id=None,
                role_id=4,
                default_branch_id=None,
                password_hash=hash_password("Pass1234!"),
            ),
            User(
                id=5,
                email="tenant@t2.example.com",
                full_name="Tenant Admin T2",
                status="active",
                tenant_id=2,
                role_id=3,
                default_branch_id=2,
                password_hash=hash_password("Pass1234!"),
            ),
            User(
                id=6,
                email="seller@t2.example.com",
                full_name="Seller T2",
                status="inactive",
                tenant_id=2,
                role_id=1,
                default_branch_id=2,
                password_hash=hash_password("Pass1234!"),
            ),
        ]
        db.add_all(users)
        db.commit()

        yield db


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def _get_test_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(db_session: Session):
    def _build(email: str) -> dict[str, str]:
        user = db_session.query(User).filter(User.email == email).one()
        token = create_access_token(str(user.id))
        return {"Authorization": f"Bearer {token}"}

    return _build
