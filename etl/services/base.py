from typing import Generic, List, Optional, Type, TypeVar

from db import SessionLocal
from settings import get_logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = get_logger(__name__)

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, session: Session, **kwargs) -> Optional[ModelType]:

        try:
            instance = self.model(**kwargs)
            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar {self.model.__name__}: {e}")
            session.rollback()
            return None
