"""
Testes essenciais para os modelos SQLAlchemy.
"""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from models.data import Data, Signal


class TestModels:
    """Testes essenciais para os modelos."""

    @pytest.mark.unit
    def test_signal_creation(self, test_session):
        """Testa criação de um sinal."""
        signal = Signal(name="test_signal")
        test_session.add(signal)
        test_session.commit()

        assert signal.id is not None
        assert signal.name == "test_signal"

    @pytest.mark.unit
    def test_data_creation(self, test_session, sample_signals):
        """Testa criação de um ponto de dados."""
        signal = sample_signals[0]
        timestamp = datetime(
            2024, 1, 1, 10, 20, 0
        )  # Timestamp diferente para evitar conflito

        data_point = Data(signal_id=signal.id, ts=timestamp, value=100.0)
        test_session.add(data_point)
        test_session.commit()

        assert data_point.signal_id == signal.id
        assert data_point.value == 100.0
        assert data_point.created_at is not None

    @pytest.mark.unit
    def test_data_timestamp_constraint(self, test_session, sample_signals):
        """Testa constraint de timestamp (deve ser intervalo de 10 minutos)."""
        signal = sample_signals[0]

        # Timestamp inválido (10:05:00)
        invalid_timestamp = datetime(2024, 1, 1, 10, 5, 0)
        data_invalid = Data(signal_id=signal.id, ts=invalid_timestamp, value=100.0)
        test_session.add(data_invalid)

        with pytest.raises(IntegrityError):
            test_session.commit()
