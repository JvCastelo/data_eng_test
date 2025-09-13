from sqlalchemy import TIMESTAMP, Column, Float, Integer, func

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
