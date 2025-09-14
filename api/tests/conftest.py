"""
Configuração global para os testes.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db import Base


@pytest.fixture(scope="session")
def test_engine():
    """Engine de teste para toda a sessão."""
    engine = create_engine(
        "sqlite:///./test.db", connect_args={"check_same_thread": False}
    )
    return engine


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Sessão de teste limpa para cada teste."""
    Base.metadata.create_all(bind=test_engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)
