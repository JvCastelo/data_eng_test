import hashlib

import pytest
from db import Base
from models.data import ApiKey, Data, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="function")
def test_db():
    engine = create_engine(
        "sqlite:///./test_models.db", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


class TestUserModel:

    def test_create_user(self, test_db):
        user = User(username="testuser")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"

    def test_user_unique_username(self, test_db):
        user1 = User(username="testuser")
        user2 = User(username="testuser")

        test_db.add(user1)
        test_db.commit()

        test_db.add(user2)
        with pytest.raises(Exception):
            test_db.commit()

    def test_user_relationship_with_api_keys(self, test_db):
        user = User(username="testuser")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        api_key = ApiKey(
            user_id=user.id, hashed_key="test-hash", description="Test Key"
        )
        test_db.add(api_key)
        test_db.commit()

        assert len(user.api_keys) == 1
        assert user.api_keys[0].description == "Test Key"


class TestApiKeyModel:

    def test_create_api_key(self, test_db):
        user = User(username="testuser")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        api_key = ApiKey(
            user_id=user.id,
            hashed_key="test-hash-123",
            description="Test API Key",
            is_active=True,
        )
        test_db.add(api_key)
        test_db.commit()
        test_db.refresh(api_key)

        assert api_key.id is not None
        assert api_key.user_id == user.id
        assert api_key.hashed_key == "test-hash-123"
        assert api_key.description == "Test API Key"
        assert api_key.is_active is True

    def test_api_key_default_values(self, test_db):
        user = User(username="testuser")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        api_key = ApiKey(user_id=user.id, hashed_key="test-hash")
        test_db.add(api_key)
        test_db.commit()
        test_db.refresh(api_key)

        assert api_key.is_active is True
        assert api_key.description is None
        assert api_key.created_at is not None

    def test_api_key_unique_hash(self, test_db):
        user = User(username="testuser")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        api_key1 = ApiKey(user_id=user.id, hashed_key="same-hash")
        api_key2 = ApiKey(user_id=user.id, hashed_key="same-hash")

        test_db.add(api_key1)
        test_db.commit()

        test_db.add(api_key2)
        with pytest.raises(Exception):
            test_db.commit()

    def test_api_key_relationship_with_user(self, test_db):
        user = User(username="testuser")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        api_key = ApiKey(
            user_id=user.id, hashed_key="test-hash", description="Test Key"
        )
        test_db.add(api_key)
        test_db.commit()
        test_db.refresh(api_key)

        assert api_key.user.username == "testuser"
        assert api_key.user.id == user.id


class TestDataModel:

    def test_create_data_record(self, test_db):
        from datetime import datetime

        data_record = Data(
            ts=datetime.now(), wind_speed=10.5, power=100.0, ambient_temperature=25.0
        )
        test_db.add(data_record)
        test_db.commit()
        test_db.refresh(data_record)

        assert data_record.id is not None
        assert data_record.wind_speed == 10.5
        assert data_record.power == 100.0
        assert data_record.ambient_temperature == 25.0
        assert data_record.created_at is not None

    def test_data_record_optional_fields(self, test_db):
        from datetime import datetime

        data_record = Data(ts=datetime.now())
        test_db.add(data_record)
        test_db.commit()
        test_db.refresh(data_record)

        assert data_record.id is not None
        assert data_record.wind_speed is None
        assert data_record.power is None
        assert data_record.ambient_temperature is None


class TestHashFunction:

    def test_hash_consistency(self):
        api_key = "test-api-key-123"
        hash1 = hashlib.sha256(api_key.encode()).hexdigest()
        hash2 = hashlib.sha256(api_key.encode()).hexdigest()

        assert hash1 == hash2

    def test_hash_different_keys(self):
        key1 = "test-key-1"
        key2 = "test-key-2"

        hash1 = hashlib.sha256(key1.encode()).hexdigest()
        hash2 = hashlib.sha256(key2.encode()).hexdigest()

        assert hash1 != hash2

    def test_hash_length(self):
        api_key = "test-api-key"
        hash_result = hashlib.sha256(api_key.encode()).hexdigest()

        assert len(hash_result) == 64
