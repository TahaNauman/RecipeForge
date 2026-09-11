import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parent.parent
TEST_DB = "recipeforge_test"
TEST_DB_URL = (
    f"postgresql+psycopg://recipeforge:recipeforge@localhost:5432/{TEST_DB}"
)
ADMIN_URL = "postgresql+psycopg://recipeforge:recipeforge@localhost:5432/postgres"

# Must be set before any app module is imported, otherwise Settings is
# instantiated with the dev DATABASE_URL and tests hit the dev database.
os.environ["DATABASE_URL"] = TEST_DB_URL


def _create_test_db() -> None:
    engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": TEST_DB}
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB}"'))
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def app_database():
    _create_test_db()

    from alembic import command
    from alembic.config import Config

    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(cfg, "head")

    yield

    from app.db.base import Base, engine

    Base.metadata.drop_all(engine)


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c