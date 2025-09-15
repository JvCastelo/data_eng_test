from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.data import Data as DataModel
from services.base import BaseService
from settings import get_logger

logger = get_logger(__name__)


class DataService(BaseService[DataModel]):

    def __init__(self):
        super().__init__(DataModel)

    def bulk_insert_data_points(
        self, session: Session, data_points: List[DataModel]
    ) -> bool:

        try:
            for data_point in data_points:
                session.merge(data_point)

            session.commit()
            logger.info(
                f"{len(data_points)} pontos de dados inseridos/atualizados com sucesso"
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir pontos de dados em lote: {e}")
            session.rollback()
            return False

    def create_data_point(
        self, session: Session, signal_id: int, timestamp: datetime, value: float
    ) -> Optional[DataModel]:

        try:
            return self.create(session, signal_id=signal_id, ts=timestamp, value=value)
        except Exception as e:
            logger.error(f"Erro ao criar ponto de dados: {e}")
            return None
