import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

from database import Base, get_db
from main import app

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///./test_vos.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
async def client():
    """Async HTTP test client for FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def seed_personas(db):
    """Seed default personas into the test database."""
    from services.review_service import PERSONAS
    from database import DbPersona

    for p in PERSONAS:
        existing = db.query(DbPersona).filter(DbPersona.id == p.id).first()
        if not existing:
            db_persona = DbPersona(
                id=p.id,
                name=p.name,
                description=p.description,
                system_prompt=p.system_prompt,
                tone=p.tone.value if hasattr(p.tone, 'value') else str(p.tone),
                focus_areas=p.focus_areas,
                color=p.color,
                weight=p.weight,
            )
            db.add(db_persona)
    db.commit()
