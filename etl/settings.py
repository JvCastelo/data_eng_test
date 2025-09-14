import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST_TARGET = os.getenv("DB_HOST_TARGET")
DB_PORT_TARGET = int(os.getenv("DB_PORT_TARGET"))
DB_NAME_TARGET = os.getenv("DB_NAME_TARGET")
DB_USER_TARGET = os.getenv("DB_USER_TARGET")
DB_PASSWORD_TARGET = os.getenv("DB_PASSWORD_TARGET")

DATABASE_URL_TARGET = f"postgresql+psycopg2://{DB_USER_TARGET}:{DB_PASSWORD_TARGET}@{DB_HOST_TARGET}:{DB_PORT_TARGET}/{DB_NAME_TARGET}"

API_BASE_URL = os.getenv("API_BASE_URL")
