from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.db import Base
from api.main import app
from api.models.data import Data as DataModel
from api.routes.data import get_db

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Setup database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def sample_data():
    """Create sample data for tests"""
    db = TestingSessionLocal()
    try:
        # Create test data
        test_data = [
            DataModel(
                ts=datetime(2025, 1, 1, 10, 0, 0),
                wind_speed=10.5,
                power=100.0,
                ambient_temperature=25.0,
            ),
            DataModel(
                ts=datetime(2025, 1, 1, 11, 0, 0),
                wind_speed=12.0,
                power=120.0,
                ambient_temperature=26.0,
            ),
            DataModel(
                ts=datetime(2025, 1, 2, 10, 0, 0),
                wind_speed=8.5,
                power=80.0,
                ambient_temperature=24.0,
            ),
            DataModel(
                ts=datetime(2025, 1, 2, 11, 0, 0),
                wind_speed=15.0,
                power=150.0,
                ambient_temperature=27.0,
            ),
        ]

        for data in test_data:
            db.add(data)
        db.commit()

        yield test_data
    finally:
        db.close()


# Testes para rota raiz
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API de dados no ar!"}


# Testes para rota de campos disponíveis
def test_get_available_fields():
    response = client.get("/api/v1/data/fields")
    assert response.status_code == 200

    fields = response.json()
    assert isinstance(fields, list)
    assert "ts" in fields
    assert "wind_speed" in fields
    assert "power" in fields
    assert "ambient_temperature" in fields


# Testes para rota de dados
def test_get_data_empty_database(setup_database):
    """Test getting data from empty database"""
    response = client.get("/api/v1/data/")
    assert response.status_code == 200

    data = response.json()
    assert data["data"] == []
    assert data["paging"]["total_items"] == 0
    assert data["paging"]["total_pages"] == 0
    assert data["paging"]["page"] == 1
    assert data["paging"]["has_next"] is False


def test_get_data_with_sample_data(setup_database, sample_data):
    """Test getting data with sample data"""
    response = client.get("/api/v1/data/")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 4
    assert data["paging"]["total_items"] == 4
    assert data["paging"]["total_pages"] == 1
    assert data["paging"]["page"] == 1
    assert data["paging"]["has_next"] is False

    # Check if data is ordered by ts desc (most recent first)
    timestamps = [item["ts"] for item in data["data"]]
    assert timestamps == sorted(timestamps, reverse=True)


def test_get_data_with_pagination(setup_database, sample_data):
    """Test pagination functionality"""
    # Test first page with 2 items
    response = client.get("/api/v1/data/?page=1&page_size=2")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 2
    assert data["paging"]["total_items"] == 4
    assert data["paging"]["total_pages"] == 2
    assert data["paging"]["page"] == 1
    assert data["paging"]["has_next"] is True

    # Test second page
    response = client.get("/api/v1/data/?page=2&page_size=2")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 2
    assert data["paging"]["page"] == 2
    assert data["paging"]["has_next"] is False


def test_get_data_with_date_filters(setup_database, sample_data):
    """Test date filtering functionality"""
    # Test with start_ts filter
    response = client.get("/api/v1/data/?start_ts=2025-01-02T00:00:00")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 2  # Only data from 2025-01-02

    # Test with end_ts filter
    response = client.get("/api/v1/data/?end_ts=2025-01-01T23:59:59")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 2  # Only data from 2025-01-01

    # Test with both filters
    response = client.get(
        "/api/v1/data/?start_ts=2025-01-01T10:30:00&end_ts=2025-01-01T11:30:00"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 1  # Only one record in this time range


def test_get_data_with_field_selection(setup_database, sample_data):
    """Test field selection functionality"""
    # Test selecting specific fields
    response = client.get("/api/v1/data/?fields=ts,wind_speed")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 4

    # Check that only selected fields are present
    first_item = data["data"][0]
    assert "ts" in first_item
    assert "wind_speed" in first_item
    assert "power" not in first_item
    assert "ambient_temperature" not in first_item


def test_get_data_with_invalid_fields(setup_database, sample_data):
    """Test error handling for invalid fields"""
    response = client.get("/api/v1/data/?fields=invalid_field,another_invalid")
    assert response.status_code == 400

    error_data = response.json()
    assert "Campos inválidos" in error_data["detail"]
    assert "invalid_field" in error_data["detail"]
    assert "another_invalid" in error_data["detail"]


def test_get_data_with_mixed_valid_invalid_fields(setup_database, sample_data):
    """Test error handling for mix of valid and invalid fields"""
    response = client.get("/api/v1/data/?fields=ts,invalid_field,power")
    assert response.status_code == 400

    error_data = response.json()
    assert "Campos inválidos" in error_data["detail"]
    assert "invalid_field" in error_data["detail"]


def test_get_data_with_empty_fields(setup_database, sample_data):
    """Test handling of empty fields parameter"""
    response = client.get("/api/v1/data/?fields=")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 4
    # Should return all fields when fields parameter is empty


def test_get_data_with_whitespace_fields(setup_database, sample_data):
    """Test handling of fields with whitespace"""
    response = client.get("/api/v1/data/?fields= ts , wind_speed , power ")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 4

    # Check that only selected fields are present
    first_item = data["data"][0]
    assert "ts" in first_item
    assert "wind_speed" in first_item
    assert "power" in first_item
    assert "ambient_temperature" not in first_item


def test_get_data_pagination_edge_cases(setup_database, sample_data):
    """Test pagination edge cases"""
    # Test page beyond available data
    response = client.get("/api/v1/data/?page=10&page_size=2")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 0
    assert data["paging"]["page"] == 10
    assert data["paging"]["has_next"] is False

    # Test page size larger than total items
    response = client.get("/api/v1/data/?page=1&page_size=100")
    assert response.status_code == 200

    data = response.json()
    assert len(data["data"]) == 4
    assert data["paging"]["total_pages"] == 1
    assert data["paging"]["has_next"] is False


def test_get_data_invalid_page_parameters():
    """Test validation of page parameters"""
    # Test negative page
    response = client.get("/api/v1/data/?page=-1")
    assert response.status_code == 422  # Validation error

    # Test zero page
    response = client.get("/api/v1/data/?page=0")
    assert response.status_code == 422  # Validation error

    # Test negative page_size
    response = client.get("/api/v1/data/?page_size=-1")
    assert response.status_code == 422  # Validation error

    # Test page_size too large
    response = client.get("/api/v1/data/?page_size=1001")
    assert response.status_code == 422  # Validation error


def test_get_data_invalid_date_format():
    """Test handling of invalid date formats"""
    response = client.get("/api/v1/data/?start_ts=invalid-date")
    assert response.status_code == 422  # Validation error

    response = client.get("/api/v1/data/?end_ts=not-a-date")
    assert response.status_code == 422  # Validation error


def test_get_data_required_fields_always_included(setup_database, sample_data):
    """Test that required fields are always included"""
    # Test with fields that don't include 'ts' (required field)
    response = client.get("/api/v1/data/?fields=wind_speed,power")
    assert response.status_code == 200

    data = response.json()
    first_item = data["data"][0]

    # 'ts' should be included even though not explicitly requested
    assert "ts" in first_item
    assert "wind_speed" in first_item
    assert "power" in first_item
    assert "ambient_temperature" not in first_item
