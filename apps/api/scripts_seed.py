from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import Tenant, Branch, Role, User, UserBranchAssignment
from app.core.security import hash_password


def run_seed(db: Session):
    if db.query(Role).count() == 0:
        db.add_all([
            Role(id=1, name="seller", description="Operador de ventas"),
            Role(id=2, name="branch_admin", description="Admin de sucursal"),
            Role(id=3, name="tenant_admin", description="Admin de negocio"),
            Role(id=4, name="platform_admin", description="Admin de plataforma"),
        ])
        db.commit()

    if db.query(Tenant).count() == 0:
        tenant = Tenant(name="Demo Food Truck", slug="demo-foodtruck", status="active")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        b1 = Branch(tenant_id=tenant.id, name="Sucursal Centro", code="CTR", status="active", address="Av. Central 123")
        b2 = Branch(tenant_id=tenant.id, name="Sucursal Norte", code="NRT", status="active", address="Calle Norte 45")
        db.add_all([b1, b2])
        db.commit()
        db.refresh(b1)
        db.refresh(b2)

        users = [
            User(email="seller@demo.com", full_name="Seller Demo", status="active", tenant_id=tenant.id, role_id=1, default_branch_id=b1.id, password_hash=hash_password("Pass1234!")),
            User(email="branch@demo.com", full_name="Branch Admin Demo", status="active", tenant_id=tenant.id, role_id=2, default_branch_id=b1.id, password_hash=hash_password("Pass1234!")),
            User(email="tenant@demo.com", full_name="Tenant Admin Demo", status="active", tenant_id=tenant.id, role_id=3, default_branch_id=b1.id, password_hash=hash_password("Pass1234!")),
            User(email="platform@demo.com", full_name="Platform Admin Demo", status="active", tenant_id=None, role_id=4, default_branch_id=None, password_hash=hash_password("Pass1234!")),
        ]
        db.add_all(users)
        db.commit()
        for user in users[:3]:
            db.refresh(user)
        db.add_all([
            UserBranchAssignment(user_id=users[0].id, branch_id=b1.id),
            UserBranchAssignment(user_id=users[1].id, branch_id=b1.id),
            UserBranchAssignment(user_id=users[2].id, branch_id=b1.id),
            UserBranchAssignment(user_id=users[0].id, branch_id=b2.id),
        ])
        db.commit()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_seed(db)
        print("Seed completed")
    finally:
        db.close()
