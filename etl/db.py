from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import que funciona tanto de dentro quanto de fora do diretório api/
from api.settings import DATABASE_URL_TARGET

engine = create_engine(DATABASE_URL_TARGET)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
