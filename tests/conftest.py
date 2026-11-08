"""
Pytest configuration and shared test fixtures.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config.settings import settings
from backend.database.session import Base, get_db
from backend.api.server import app
from backend.cache.memory import cache_instance

# Test In-Memory SQLite Database
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes schema once per test session."""
    import backend.database.models  # Register models
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Provides isolated test database session per test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def reset_cache():
    """Clears in-memory sliding window cache before each test."""
    cache_instance.clear()
    yield
    cache_instance.clear()


@pytest_asyncio.fixture
async def async_client(db_session):
    """Provides async HTTP client configured with test database dependency overrides."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

