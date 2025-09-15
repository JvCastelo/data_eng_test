from datetime import datetime

import pytest
from models.data import Data, Signal
from sqlalchemy.exc import IntegrityError


class TestModels:

    @pytest.mark.unit
    def test_signal_creation(self, test_session):
        signal = Signal(name="test_signal")
        test_session.add(signal)
        test_session.commit()

        assert signal.id is not None
        assert signal.name == "test_signal"

    @pytest.mark.unit
    def test_data_creation(self, test_session, sample_signals):
        signal = sample_signals[0]
        timestamp = datetime(2024, 1, 1, 10, 20, 0)

        data_point = Data(signal_id=signal.id, ts=timestamp, value=100.0)
        test_session.add(data_point)
        test_session.commit()

        assert data_point.signal_id == signal.id
        assert data_point.value == 100.0
        assert data_point.created_at is not None

    @pytest.mark.unit
    def test_data_timestamp_constraint(self, test_session, sample_signals):
        signal = sample_signals[0]

        invalid_timestamp = datetime(2024, 1, 1, 10, 5, 0)
        data_invalid = Data(signal_id=signal.id, ts=invalid_timestamp, value=100.0)
        test_session.add(data_invalid)

        with pytest.raises(IntegrityError):
            test_session.commit()
