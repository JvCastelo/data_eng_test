import pytest
from db import Base, SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///./test.db", connect_args={"check_same_thread": False}
    )
    return engine


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    Base.metadata.create_all(bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)
