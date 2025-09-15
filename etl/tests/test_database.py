from datetime import datetime

import pytest
from models.data import Data, Signal
from sqlalchemy.exc import IntegrityError


class TestDatabase:

    @pytest.mark.database
    def test_create_tables(self, test_engine):
        from sqlalchemy import inspect

        inspector = inspect(test_engine)
        tables = inspector.get_table_names()

        assert "signal" in tables
        assert "data" in tables

    @pytest.mark.database
    def test_signal_crud(self, test_session):
        signal = Signal(name="test_signal")
        test_session.add(signal)
        test_session.commit()

        retrieved = (
            test_session.query(Signal).filter(Signal.name == "test_signal").first()
        )
        assert retrieved is not None
        assert retrieved.name == "test_signal"

    @pytest.mark.database
    def test_data_constraint(self, test_session, sample_signals):
        signal = sample_signals[0]

        invalid_data = Data(
            signal_id=signal.id,
            ts=datetime(2024, 1, 1, 10, 5, 0),
            value=100.0,
        )

        test_session.add(invalid_data)

        with pytest.raises(IntegrityError):
            test_session.commit()
