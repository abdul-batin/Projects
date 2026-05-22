"""Test configuration and fixtures for pytest."""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "Server"))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from db import Base, get_db
from Server.main import app


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_wall_data():
    """Sample wall data for testing."""
    return {
        "name": "Test Wall",
        "geometry": {
            "coordinates": [[0, 0], [5, 0], [5, 5], [0, 5]]
        }
    }


@pytest.fixture
def sample_obstacle_data():
    """Sample obstacle data for testing."""
    return {
        "type": "window",
        "geometry": {
            "coordinates": [[1, 1], [2, 1], [2, 2], [1, 2]]
        }
    }


@pytest.fixture
def sample_plan_request():
    """Sample plan request for testing."""
    return {
        "resolution": 0.1
    }
