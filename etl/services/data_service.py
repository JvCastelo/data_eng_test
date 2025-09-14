from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from models.data import Data as DataModel
from services.base import BaseService
from settings import get_logger

logger = get_logger(__name__)


class DataService(BaseService[DataModel]):
    """
    Serviço para operações relacionadas aos dados.
    """

    def __init__(self):
        super().__init__(DataModel)

    def get_by_signal_and_timestamp(
        self, session: Session, signal_id: int, timestamp: datetime
    ) -> Optional[DataModel]:
        """
        Busca um dado específico por signal_id e timestamp.
        """
        try:
            return (
                session.query(DataModel)
                .filter(
                    and_(DataModel.signal_id == signal_id, DataModel.ts == timestamp)
                )
                .first()
            )
        except Exception as e:
            logger.error(
                f"Erro ao buscar dado por signal_id {signal_id} e timestamp {timestamp}: {e}"
            )
            return None

    def get_by_signal_id(self, session: Session, signal_id: int) -> List[DataModel]:
        """
        Busca todos os dados de um sinal específico.
        """
        try:
            return (
                session.query(DataModel).filter(DataModel.signal_id == signal_id).all()
            )
        except Exception as e:
            logger.error(f"Erro ao buscar dados por signal_id {signal_id}: {e}")
            return []

    def get_by_timestamp_range(
        self, session: Session, start_ts: datetime, end_ts: datetime
    ) -> List[DataModel]:
        """
        Busca dados dentro de um intervalo de tempo.
        """
        try:
            return (
                session.query(DataModel)
                .filter(and_(DataModel.ts >= start_ts, DataModel.ts <= end_ts))
                .all()
            )
        except Exception as e:
            logger.error(
                f"Erro ao buscar dados no intervalo {start_ts} - {end_ts}: {e}"
            )
            return []

    def get_by_signal_and_timestamp_range(
        self, session: Session, signal_id: int, start_ts: datetime, end_ts: datetime
    ) -> List[DataModel]:
        """
        Busca dados de um sinal específico dentro de um intervalo de tempo.
        """
        try:
            return (
                session.query(DataModel)
                .filter(
                    and_(
                        DataModel.signal_id == signal_id,
                        DataModel.ts >= start_ts,
                        DataModel.ts <= end_ts,
                    )
                )
                .all()
            )
        except Exception as e:
            logger.error(
                f"Erro ao buscar dados do signal_id {signal_id} no intervalo {start_ts} - {end_ts}: {e}"
            )
            return []

    def bulk_insert_data_points(
        self, session: Session, data_points: List[DataModel]
    ) -> bool:
        """
        Insere múltiplos pontos de dados de forma eficiente.
        Usado principalmente no processo de ETL.
        """
        try:
            session.add_all(data_points)
            session.commit()
            logger.info(f"{len(data_points)} pontos de dados inseridos com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao inserir pontos de dados em lote: {e}")
            session.rollback()
            return False

    def create_data_point(
        self, session: Session, signal_id: int, timestamp: datetime, value: float
    ) -> Optional[DataModel]:
        """
        Cria um novo ponto de dados.
        """
        try:
            return self.create(session, signal_id=signal_id, ts=timestamp, value=value)
        except Exception as e:
            logger.error(f"Erro ao criar ponto de dados: {e}")
            return None

    def delete_by_timestamp_range(
        self, session: Session, start_ts: datetime, end_ts: datetime
    ) -> int:
        """
        Remove dados dentro de um intervalo de tempo.
        Retorna o número de registros removidos.
        """
        try:
            deleted_count = (
                session.query(DataModel)
                .filter(and_(DataModel.ts >= start_ts, DataModel.ts <= end_ts))
                .delete()
            )
            session.commit()
            logger.info(
                f"{deleted_count} registros removidos no intervalo {start_ts} - {end_ts}"
            )
            return deleted_count
        except Exception as e:
            logger.error(
                f"Erro ao remover dados no intervalo {start_ts} - {end_ts}: {e}"
            )
            session.rollback()
            return 0
