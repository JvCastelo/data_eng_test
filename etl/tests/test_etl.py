"""
Testes essenciais para a classe DataETL.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from main import DataETL
from models.data import Data, Signal


class TestETL:
    """Testes essenciais para o ETL."""

    @pytest.fixture
    def etl_processor(self):
        """Instância da classe DataETL para testes."""
        return DataETL()

    @pytest.mark.unit
    def test_init(self, etl_processor):
        """Testa inicialização da classe."""
        assert etl_processor.api_base_url is not None
        assert etl_processor.client is not None

    @pytest.mark.unit
    def test_transform_data_success(self, etl_processor, sample_raw_data):
        """Testa transformação de dados com sucesso."""
        result = etl_processor.transform_data(sample_raw_data)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "ts" in result.columns
        assert "wind_speed_mean" in result.columns
        assert "power_mean" in result.columns

    @pytest.mark.unit
    def test_load_data_success(
        self, etl_processor, test_session, sample_transformed_data, sample_signals
    ):
        """Testa carregamento de dados com sucesso."""
        # Cria DataFrame simplificado apenas com sinais que existem
        simple_df = sample_transformed_data[
            ["ts", "wind_speed_mean", "power_mean"]
        ].copy()

        # Teste
        etl_processor.load_data(test_session, simple_df)

        # Verifica que dados foram salvos
        saved_data = test_session.query(Data).all()
        assert len(saved_data) > 0
