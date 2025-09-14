import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST_SOURCE = os.getenv("DB_HOST_SOURCE")
DB_PORT_SOURCE = int(os.getenv("DB_PORT_SOURCE"))
DB_NAME_SOURCE = os.getenv("DB_NAME_SOURCE")
DB_USER_SOURCE = os.getenv("DB_USER_SOURCE")
DB_PASSWORD_SOURCE = os.getenv("DB_PASSWORD_SOURCE")

DATABASE_URL_SOURCE = f"postgresql+psycopg2://{DB_USER_SOURCE}:{DB_PASSWORD_SOURCE}@{DB_HOST_SOURCE}:{DB_PORT_SOURCE}/{DB_NAME_SOURCE}"
