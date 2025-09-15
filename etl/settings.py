import logging
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_HOST_TARGET = os.getenv("DB_HOST_TARGET")
DB_PORT_TARGET = int(os.getenv("DB_PORT_TARGET"))
DB_NAME_TARGET = os.getenv("DB_NAME_TARGET")
DB_USER_TARGET = os.getenv("DB_USER_TARGET")
DB_PASSWORD_TARGET = os.getenv("DB_PASSWORD_TARGET")

DATABASE_URL_TARGET = f"postgresql+psycopg2://{DB_USER_TARGET}:{DB_PASSWORD_TARGET}@{DB_HOST_TARGET}:{DB_PORT_TARGET}/{DB_NAME_TARGET}"


API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOG_FORMAT = os.getenv(
    "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOG_DATE_FORMAT = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")


def setup_logging(level: Optional[str] = None) -> None:

    log_level = level or LOG_LEVEL

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        force=True,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
