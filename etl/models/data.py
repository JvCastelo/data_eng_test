from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    and_,
    cast,
    func,
)
from sqlalchemy.orm import relationship

from db import Base


class Signal(Base):
    __tablename__ = "signal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True, unique=True)

    data_points = relationship(
        "Data", back_populates="signal", cascade="all, delete-orphan"
    )


class Data(Base):
    __tablename__ = "data"

    signal_id = Column(Integer, ForeignKey("signal.id"), primary_key=True, index=True)
    ts = Column(TIMESTAMP, nullable=False, index=True, primary_key=True)
    value = Column(Float)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    signal = relationship("Signal", back_populates="data_points")

    __table_args__ = (
        CheckConstraint(
            and_(
                cast(func.extract("minute", ts), Integer) % 10 == 0,
                func.extract("second", ts) == 0,
            ),
            name="ts_must_be_exact_10_min_interval",
        ),
    )
