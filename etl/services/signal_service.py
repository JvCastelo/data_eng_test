from typing import Dict, List, Optional

from models.data import Signal as SignalModel
from services.base import BaseService
from settings import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)


class SignalService(BaseService[SignalModel]):

    def __init__(self):
        super().__init__(SignalModel)

    def get_signals_map(self, session: Session) -> Dict[str, int]:

        try:
            signals = session.query(SignalModel).all()
            return {signal.name: signal.id for signal in signals}
        except Exception as e:
            logger.error(f"Erro ao criar mapa de sinais: {e}")
            return {}

    def get_all_names(self, session: Session) -> List[str]:

        try:
            signals = session.query(SignalModel.name).all()
            return [signal.name for signal in signals]
        except Exception as e:
            logger.error(f"Erro ao buscar nomes dos sinais: {e}")
            return []
