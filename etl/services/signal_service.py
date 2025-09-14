from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from models.data import Signal as SignalModel
from services.base import BaseService
from settings import get_logger

logger = get_logger(__name__)


class SignalService(BaseService[SignalModel]):
    """
    Serviço para operações relacionadas aos sinais.
    """

    def __init__(self):
        super().__init__(SignalModel)

    def get_by_name(self, session: Session, name: str) -> Optional[SignalModel]:
        """
        Busca um sinal pelo nome.
        """
        try:
            return session.query(SignalModel).filter(SignalModel.name == name).first()
        except Exception as e:
            logger.error(f"Erro ao buscar sinal por nome '{name}': {e}")
            return None

    def get_signals_map(self, session: Session) -> Dict[str, int]:
        """
        Retorna um dicionário mapeando nome do sinal para seu ID.
        Usado principalmente no processo de ETL.
        """
        try:
            signals = session.query(SignalModel).all()
            return {signal.name: signal.id for signal in signals}
        except Exception as e:
            logger.error(f"Erro ao criar mapa de sinais: {e}")
            return {}

    def create_or_get_by_name(
        self, session: Session, name: str
    ) -> Optional[SignalModel]:
        """
        Cria um novo sinal se não existir, ou retorna o existente.
        """
        try:
            # Primeiro tenta buscar o sinal existente
            signal = self.get_by_name(session, name)
            if signal:
                return signal

            # Se não existir, cria um novo
            signal = self.create(session, name=name)
            if signal:
                logger.info(f"Sinal '{name}' criado com ID {signal.id}")
            return signal
        except Exception as e:
            logger.error(f"Erro ao criar/buscar sinal '{name}': {e}")
            return None

    def get_all_names(self, session: Session) -> List[str]:
        """
        Retorna uma lista com todos os nomes de sinais.
        """
        try:
            signals = session.query(SignalModel.name).all()
            return [signal.name for signal in signals]
        except Exception as e:
            logger.error(f"Erro ao buscar nomes dos sinais: {e}")
            return []
