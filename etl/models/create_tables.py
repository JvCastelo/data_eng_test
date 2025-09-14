from sqlalchemy import create_engine

import models.data  # Importa os modelos para registrar no Base
from db import Base
from settings import DATABASE_URL_TARGET

engine = create_engine(DATABASE_URL_TARGET)

try:
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")
except Exception as e:
    print(f"Error creating tables: {e}")
