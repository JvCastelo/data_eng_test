from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from db import Base


class Data(Base):
    """
    Modelo SQLAlchemy que representa a tabela 'data' no banco de dados.
    """

    __tablename__ = "data"

    id = Column(Integer, primary_key=True)
    ts = Column(TIMESTAMP, nullable=False, index=True)
    wind_speed = Column(Float)
    power = Column(Float)
    ambient_temperature = Column(Float)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True, nullable=False)

    api_keys = relationship(
        "ApiKey", back_populates="user", cascade="all, delete-orphan"
    )


class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    hashed_key = Column(String, unique=True, index=True, nullable=False)

    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="api_keys")
