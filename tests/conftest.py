import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nda_app.database import Base, get_db
from nda_app.main import app
from nda_app.models.nda import NDA, Jurisdiction  # noqa: F401 — register models
from nda_app.services.seed import seed_jurisdictions
from fastapi.testclient import TestClient

engine = create_engine(
    "sqlite:///./data/test.db", connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture()
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    seed_jurisdictions(session)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    """FastAPI test client with overridden DB dependency."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
