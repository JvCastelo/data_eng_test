from sqlalchemy import create_engine

from etl.db import Base
from etl.settings import DATABASE_URL_TARGET

engine = create_engine(DATABASE_URL_TARGET)

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error creating tables: {e}")
