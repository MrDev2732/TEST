from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.models.models import Branch, Role, Tenant, User
from scripts_seed import run_seed


def test_migration_and_seed_in_isolated_db(tmp_path):
    db_file = tmp_path / "isolated.db"
    database_url = f"sqlite:///{db_file}"

    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    cfg = Config(str(alembic_ini))
    cfg.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(cfg, "head")

    engine = create_engine(database_url)
    inspector = inspect(engine)

    assert set(inspector.get_table_names()) >= {
        "tenants",
        "branches",
        "roles",
        "users",
        "user_branch_assignments",
    }

    with Session(engine) as db:
        run_seed(db)
        run_seed(db)

        assert db.query(Role).count() == 4
        assert db.query(Tenant).count() == 1
        assert db.query(Branch).count() == 2
        assert db.query(User).count() == 4
