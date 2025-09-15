import os
import sys
from datetime import datetime

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import Base, SessionLocal
from models.data import Data, Signal


@pytest.fixture(scope="session")
def test_engine():

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def test_session(test_engine):

    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def sample_signals(test_session):

    # Limpa sinais existentes primeiro
    test_session.query(Signal).delete()
    test_session.commit()

    signals = [
        Signal(name="wind_speed_mean"),
        Signal(name="wind_speed_min"),
        Signal(name="power_mean"),
        Signal(name="power_max"),
    ]

    for signal in signals:
        test_session.add(signal)
    test_session.commit()

    return signals


@pytest.fixture(scope="function")
def sample_data(test_session, sample_signals):

    # Limpa dados existentes primeiro
    test_session.query(Data).delete()
    test_session.commit()

    signal_map = {s.name: s.id for s in sample_signals}

    data_points = [
        Data(
            signal_id=signal_map["wind_speed_mean"],
            ts=datetime(2024, 1, 1, 10, 0, 0),
            value=15.5,
        ),
        Data(
            signal_id=signal_map["power_mean"],
            ts=datetime(2024, 1, 1, 10, 10, 0),  # Timestamp diferente
            value=1200.0,
        ),
    ]

    for data_point in data_points:
        test_session.add(data_point)
    test_session.commit()

    return data_points


@pytest.fixture
def sample_raw_data():

    return [
        {
            "ts": "2024-01-01T10:00:00Z",
            "wind_speed": 15.5,
            "power": 1200.0,
            "ambient_temperature": 25.0,
        },
        {
            "ts": "2024-01-01T10:05:00Z",
            "wind_speed": 16.2,
            "power": 1250.0,
            "ambient_temperature": 25.5,
        },
        {
            "ts": "2024-01-01T10:10:00Z",
            "wind_speed": 14.8,
            "power": 1180.0,
            "ambient_temperature": 24.8,
        },
    ]


@pytest.fixture
def sample_transformed_data():

    return pd.DataFrame(
        {
            "ts": [
                datetime(2024, 1, 1, 10, 0, 0),
                datetime(2024, 1, 1, 10, 10, 0),
            ],
            "wind_speed_mean": [15.5, 14.8],
            "wind_speed_min": [15.5, 14.8],
            "wind_speed_max": [16.2, 14.8],
            "power_mean": [1200.0, 1180.0],
            "power_min": [1200.0, 1180.0],
            "power_max": [1250.0, 1180.0],
        }
    )


@pytest.fixture
def mock_httpx_client():

    from unittest.mock import Mock

    mock_response = Mock()
    mock_response.json.return_value = {
        "data": [
            {
                "ts": "2024-01-01T10:00:00Z",
                "wind_speed": 15.5,
                "power": 1200.0,
            }
        ],
        "paging": {"total_pages": 1},
    }
    mock_response.raise_for_status.return_value = None

    mock_client = Mock()
    mock_client.get.return_value = mock_response

    return mock_client
