"""
Testes automatizados para o sistema de autenticação por API Key.
"""

import hashlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base, SessionLocal
from main import app
from models.data import ApiKey, User

# Configuração do banco de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Fixture para criar um banco de teste limpo para cada teste."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(test_db):
    """Fixture para criar um usuário de teste."""
    user = User(username="testuser")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_api_key(test_db, test_user):
    """Fixture para criar uma API key de teste."""
    api_key_plain = "test-api-key-123456789"
    hashed_key = hashlib.sha256(api_key_plain.encode()).hexdigest()

    api_key = ApiKey(
        user_id=test_user.id,
        hashed_key=hashed_key,
        description="Test API Key",
        is_active=True,
    )
    test_db.add(api_key)
    test_db.commit()
    test_db.refresh(api_key)

    return api_key_plain, api_key


@pytest.fixture(scope="function")
def client():
    """Fixture para criar um cliente de teste."""
    return TestClient(app)


class TestAuthentication:
    """Testes para o sistema de autenticação."""

    def test_verify_valid_api_key(self, client, test_api_key):
        """Testa verificação de API key válida."""
        api_key_plain, _ = test_api_key

        response = client.get(
            "/api/v1/auth/verify", headers={"Authorization": f"Bearer {api_key_plain}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "testuser"
        assert "API key válida" in data["message"]

    def test_verify_invalid_api_key(self, client):
        """Testa verificação de API key inválida."""
        response = client.get(
            "/api/v1/auth/verify", headers={"Authorization": "Bearer invalid-key"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "API Key inválida" in data["detail"]

    def test_verify_no_authorization_header(self, client):
        """Testa requisição sem header de autorização."""
        response = client.get("/api/v1/auth/verify")

        assert response.status_code == 403
        data = response.json()
        assert "Not authenticated" in data["detail"]

    def test_verify_malformed_authorization_header(self, client):
        """Testa header de autorização malformado."""
        response = client.get(
            "/api/v1/auth/verify", headers={"Authorization": "InvalidFormat test-key"}
        )

        assert response.status_code == 403

    def test_protected_endpoint_with_valid_key(self, client, test_api_key):
        """Testa acesso a endpoint protegido com API key válida."""
        api_key_plain, _ = test_api_key

        response = client.get(
            "/api/v1/data/fields", headers={"Authorization": f"Bearer {api_key_plain}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "ts" in data
        assert "wind_speed" in data

    def test_protected_endpoint_without_auth(self, client):
        """Testa acesso a endpoint protegido sem autenticação."""
        response = client.get("/api/v1/data/fields")

        assert response.status_code == 403
        data = response.json()
        assert "Not authenticated" in data["detail"]

    def test_protected_endpoint_with_invalid_key(self, client):
        """Testa acesso a endpoint protegido com API key inválida."""
        response = client.get(
            "/api/v1/data/fields", headers={"Authorization": "Bearer invalid-key"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "API Key inválida" in data["detail"]

    def test_data_endpoint_with_valid_key(self, client, test_api_key):
        """Testa endpoint de dados com API key válida."""
        api_key_plain, _ = test_api_key

        response = client.get(
            "/api/v1/data/", headers={"Authorization": f"Bearer {api_key_plain}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data

    def test_data_endpoint_pagination(self, client, test_api_key):
        """Testa paginação no endpoint de dados."""
        api_key_plain, _ = test_api_key

        response = client.get(
            "/api/v1/data/?page=1&page_size=10",
            headers={"Authorization": f"Bearer {api_key_plain}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_inactive_api_key(self, client, test_db, test_user):
        """Testa API key inativa."""
        # Cria uma API key inativa
        api_key_plain = "inactive-test-key"
        hashed_key = hashlib.sha256(api_key_plain.encode()).hexdigest()

        api_key = ApiKey(
            user_id=test_user.id,
            hashed_key=hashed_key,
            description="Inactive Test Key",
            is_active=False,  # Key inativa
        )
        test_db.add(api_key)
        test_db.commit()

        # Tenta usar a key inativa
        response = client.get(
            "/api/v1/auth/verify", headers={"Authorization": f"Bearer {api_key_plain}"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "API Key inválida" in data["detail"]

    def test_nonexistent_user(self, client, test_db):
        """Testa API key com usuário inexistente."""
        # Cria uma API key com user_id inexistente
        api_key_plain = "orphan-test-key"
        hashed_key = hashlib.sha256(api_key_plain.encode()).hexdigest()

        api_key = ApiKey(
            user_id=99999,  # User ID que não existe
            hashed_key=hashed_key,
            description="Orphan Test Key",
            is_active=True,
        )
        test_db.add(api_key)
        test_db.commit()

        # Tenta usar a key
        response = client.get(
            "/api/v1/auth/verify", headers={"Authorization": f"Bearer {api_key_plain}"}
        )

        # Deve falhar porque o usuário não existe
        assert response.status_code == 401


class TestDataEndpoints:
    """Testes para endpoints de dados."""

    def test_fields_endpoint(self, client, test_api_key):
        """Testa endpoint de campos disponíveis."""
        api_key_plain, _ = test_api_key

        response = client.get(
            "/api/v1/data/fields", headers={"Authorization": f"Bearer {api_key_plain}"}
        )

        assert response.status_code == 200
        fields = response.json()
        expected_fields = ["ts", "wind_speed", "power", "ambient_temperature"]

        for field in expected_fields:
            assert field in fields

    def test_data_endpoint_empty_database(self, client, test_api_key):
        """Testa endpoint de dados com banco vazio."""
        api_key_plain, _ = test_api_key

        response = client.get(
            "/api/v1/data/", headers={"Authorization": f"Bearer {api_key_plain}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["data"] == []
        assert data["page"] == 1
        assert data["page_size"] == 25

    def test_data_endpoint_invalid_page(self, client, test_api_key):
        """Testa endpoint de dados com página inválida."""
        api_key_plain, _ = test_api_key

        response = client.get(
            "/api/v1/data/?page=0", headers={"Authorization": f"Bearer {api_key_plain}"}
        )

        assert response.status_code == 422  # Validation error

    def test_data_endpoint_invalid_page_size(self, client, test_api_key):
        """Testa endpoint de dados com tamanho de página inválido."""
        api_key_plain, _ = test_api_key

        response = client.get(
            "/api/v1/data/?page_size=2000",
            headers={"Authorization": f"Bearer {api_key_plain}"},
        )

        assert response.status_code == 422  # Validation error


class TestRootEndpoint:
    """Testes para endpoint raiz."""

    def test_root_endpoint(self, client):
        """Testa endpoint raiz (não protegido)."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "API de dados no ar!" in data["message"]

    def test_docs_endpoint(self, client):
        """Testa endpoint de documentação."""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_endpoint(self, client):
        """Testa endpoint OpenAPI."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
