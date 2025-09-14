"""
Testes para os serviços de banco de dados.
"""

from datetime import datetime

import pytest

from models.data import Data, Signal
from services import DataService, SignalService


class TestSignalService:
    """Testes para SignalService."""

    @pytest.fixture
    def signal_service(self):
        """Instância do SignalService para testes."""
        return SignalService()

    @pytest.mark.database
    def test_create_signal(self, signal_service, test_session):
        """Testa criação de um sinal."""
        signal = signal_service.create(test_session, name="test_signal")

        assert signal is not None
        assert signal.name == "test_signal"
        assert signal.id is not None

    @pytest.mark.database
    def test_get_by_name(self, signal_service, test_session):
        """Testa busca de sinal por nome."""
        # Cria um sinal primeiro
        signal_service.create(test_session, name="test_signal_by_name")

        # Busca o sinal
        found_signal = signal_service.get_by_name(test_session, "test_signal_by_name")

        assert found_signal is not None
        assert found_signal.name == "test_signal_by_name"

    @pytest.mark.database
    def test_get_signals_map(self, signal_service, test_session):
        """Testa criação do mapa de sinais."""
        # Cria alguns sinais
        signal_service.create(test_session, name="signal1")
        signal_service.create(test_session, name="signal2")

        # Obtém o mapa
        signal_map = signal_service.get_signals_map(test_session)

        assert "signal1" in signal_map
        assert "signal2" in signal_map
        assert isinstance(signal_map["signal1"], int)
        assert isinstance(signal_map["signal2"], int)

    @pytest.mark.database
    def test_create_or_get_by_name_existing(self, signal_service, test_session):
        """Testa criação/busca de sinal existente."""
        # Cria um sinal
        original_signal = signal_service.create(test_session, name="existing_signal")

        # Tenta criar/buscar o mesmo sinal
        found_signal = signal_service.create_or_get_by_name(
            test_session, "existing_signal"
        )

        assert found_signal is not None
        assert found_signal.id == original_signal.id
        assert found_signal.name == "existing_signal"

    @pytest.mark.database
    def test_create_or_get_by_name_new(self, signal_service, test_session):
        """Testa criação/busca de sinal novo."""
        # Tenta criar/buscar um sinal que não existe
        new_signal = signal_service.create_or_get_by_name(test_session, "new_signal")

        assert new_signal is not None
        assert new_signal.name == "new_signal"
        assert new_signal.id is not None

    @pytest.mark.database
    def test_get_all_names(self, signal_service, test_session):
        """Testa listagem de todos os nomes de sinais."""
        # Cria alguns sinais
        signal_service.create(test_session, name="signal_a")
        signal_service.create(test_session, name="signal_b")

        # Obtém todos os nomes
        names = signal_service.get_all_names(test_session)

        assert "signal_a" in names
        assert "signal_b" in names
        assert isinstance(names, list)


class TestDataService:
    """Testes para DataService."""

    @pytest.fixture
    def data_service(self):
        """Instância do DataService para testes."""
        return DataService()

    @pytest.mark.database
    def test_create_data_point(self, data_service, test_session, sample_signals):
        """Testa criação de um ponto de dados."""
        signal = sample_signals[0]
        timestamp = datetime(2024, 1, 1, 10, 0, 0)

        data_point = data_service.create_data_point(
            test_session, signal.id, timestamp, 100.5
        )

        assert data_point is not None
        assert data_point.signal_id == signal.id
        assert data_point.ts == timestamp
        assert data_point.value == 100.5

    @pytest.mark.database
    def test_get_by_signal_and_timestamp(
        self, data_service, test_session, sample_signals
    ):
        """Testa busca de dado por signal_id e timestamp."""
        signal = sample_signals[0]
        timestamp = datetime(2024, 1, 1, 10, 0, 0)

        # Cria um ponto de dados
        data_service.create_data_point(test_session, signal.id, timestamp, 100.5)

        # Busca o ponto de dados
        found_data = data_service.get_by_signal_and_timestamp(
            test_session, signal.id, timestamp
        )

        assert found_data is not None
        assert found_data.signal_id == signal.id
        assert found_data.ts == timestamp
        assert found_data.value == 100.5

    @pytest.mark.database
    def test_get_by_signal_id(self, data_service, test_session, sample_signals):
        """Testa busca de dados por signal_id."""
        signal = sample_signals[0]

        # Cria alguns pontos de dados
        timestamps = [
            datetime(2024, 1, 1, 10, 0, 0),
            datetime(2024, 1, 1, 10, 10, 0),
            datetime(2024, 1, 1, 10, 20, 0),
        ]

        for ts in timestamps:
            data_service.create_data_point(test_session, signal.id, ts, 100.0)

        # Busca todos os dados do sinal
        data_points = data_service.get_by_signal_id(test_session, signal.id)

        assert len(data_points) >= 3  # Pode ter mais dados de outros testes
        signal_data = [dp for dp in data_points if dp.signal_id == signal.id]
        assert len(signal_data) >= 3

    @pytest.mark.database
    def test_get_by_timestamp_range(self, data_service, test_session, sample_signals):
        """Testa busca de dados por intervalo de tempo."""
        signal = sample_signals[0]

        # Cria pontos de dados em diferentes horários
        timestamps = [
            datetime(2024, 1, 1, 9, 0, 0),  # Fora do range
            datetime(2024, 1, 1, 10, 0, 0),  # Dentro do range
            datetime(2024, 1, 1, 11, 0, 0),  # Dentro do range
            datetime(2024, 1, 1, 12, 0, 0),  # Fora do range
        ]

        for ts in timestamps:
            data_service.create_data_point(test_session, signal.id, ts, 100.0)

        # Busca dados no intervalo
        start_ts = datetime(2024, 1, 1, 10, 0, 0)
        end_ts = datetime(2024, 1, 1, 11, 30, 0)

        data_points = data_service.get_by_timestamp_range(
            test_session, start_ts, end_ts
        )

        # Deve encontrar pelo menos os dados dentro do range
        timestamps_in_range = [ts for ts in timestamps if start_ts <= ts <= end_ts]
        assert len(data_points) >= len(timestamps_in_range)

    @pytest.mark.database
    def test_bulk_insert_data_points(self, data_service, test_session, sample_signals):
        """Testa inserção em lote de pontos de dados."""
        signal = sample_signals[0]

        # Prepara dados para inserção em lote
        data_points = []
        for i in range(5):
            timestamp = datetime(2024, 1, 1, 10, i * 10, 0)
            data_points.append(Data(signal_id=signal.id, ts=timestamp, value=100.0 + i))

        # Insere em lote
        success = data_service.bulk_insert_data_points(test_session, data_points)

        assert success is True

        # Verifica se os dados foram inseridos
        inserted_data = data_service.get_by_signal_id(test_session, signal.id)
        assert len(inserted_data) >= 5

    @pytest.mark.database
    def test_delete_by_timestamp_range(
        self, data_service, test_session, sample_signals
    ):
        """Testa remoção de dados por intervalo de tempo."""
        signal = sample_signals[0]

        # Cria alguns pontos de dados
        timestamps = [
            datetime(2024, 1, 1, 10, 0, 0),
            datetime(2024, 1, 1, 10, 10, 0),
            datetime(2024, 1, 1, 10, 20, 0),
        ]

        for ts in timestamps:
            data_service.create_data_point(test_session, signal.id, ts, 100.0)

        # Remove dados no intervalo
        start_ts = datetime(2024, 1, 1, 10, 5, 0)
        end_ts = datetime(2024, 1, 1, 10, 15, 0)

        deleted_count = data_service.delete_by_timestamp_range(
            test_session, start_ts, end_ts
        )

        assert deleted_count > 0

