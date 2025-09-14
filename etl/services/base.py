from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from db import SessionLocal
from settings import get_logger

logger = get_logger(__name__)

ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Classe base para serviços que fornece operações CRUD básicas.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_session(self) -> Session:
        """
        Retorna uma nova sessão do banco de dados.
        """
        return SessionLocal()

    def get_by_id(self, session: Session, id: int) -> Optional[ModelType]:
        """
        Busca um registro por ID.
        """
        try:
            return session.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar {self.model.__name__} por ID {id}: {e}")
            return None

    def get_all(self, session: Session) -> List[ModelType]:
        """
        Busca todos os registros.
        """
        try:
            return session.query(self.model).all()
        except SQLAlchemyError as e:
            logger.error(f"Erro ao buscar todos os {self.model.__name__}: {e}")
            return []

    def create(self, session: Session, **kwargs) -> Optional[ModelType]:
        """
        Cria um novo registro.
        """
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

    def create_many(self, session: Session, data_list: List[dict]) -> List[ModelType]:
        """
        Cria múltiplos registros.
        """
        try:
            instances = [self.model(**data) for data in data_list]
            session.add_all(instances)
            session.commit()
            return instances
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar múltiplos {self.model.__name__}: {e}")
            session.rollback()
            return []

    def update(self, session: Session, id: int, **kwargs) -> Optional[ModelType]:
        """
        Atualiza um registro existente.
        """
        try:
            instance = session.query(self.model).filter(self.model.id == id).first()
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                session.commit()
                session.refresh(instance)
                return instance
            return None
        except SQLAlchemyError as e:
            logger.error(f"Erro ao atualizar {self.model.__name__} ID {id}: {e}")
            session.rollback()
            return None

    def delete(self, session: Session, id: int) -> bool:
        """
        Remove um registro por ID.
        """
        try:
            instance = session.query(self.model).filter(self.model.id == id).first()
            if instance:
                session.delete(instance)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Erro ao deletar {self.model.__name__} ID {id}: {e}")
            session.rollback()
            return False
