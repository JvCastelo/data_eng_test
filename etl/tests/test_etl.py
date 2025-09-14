"""
Testes essenciais para a classe DataETL.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import httpx
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
        assert hasattr(etl_processor, "api_key")

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

    @pytest.mark.unit
    def test_extract_available_fields_no_api_key(self, etl_processor):
        """Testa comportamento quando API_KEY não está configurada."""
        with patch.object(etl_processor, "api_key", None):
            result = etl_processor.extract_available_fields()
            assert result == {}

    @pytest.mark.unit
    def test_extract_data_no_api_key(self, etl_processor):
        """Testa comportamento quando API_KEY não está configurada."""
        with patch.object(etl_processor, "api_key", None):
            result = etl_processor.extract_data(
                datetime(2024, 1, 1), datetime(2024, 1, 2), ["wind_speed"]
            )
            assert result == []

    @pytest.mark.unit
    def test_extract_available_fields_auth_error(self, etl_processor):
        """Testa tratamento de erro de autenticação."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=Mock(), response=mock_response
        )

        with patch.object(etl_processor.client, "get", return_value=mock_response):
            result = etl_processor.extract_available_fields()
            assert result == {}

    @pytest.mark.unit
    def test_extract_data_auth_error(self, etl_processor):
        """Testa tratamento de erro de autenticação na extração de dados."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Forbidden", request=Mock(), response=mock_response
        )

        with patch.object(etl_processor.client, "get", return_value=mock_response):
            result = etl_processor.extract_data(
                datetime(2024, 1, 1), datetime(2024, 1, 2), ["wind_speed"]
            )
            assert result == []

    @pytest.mark.unit
    def test_client_headers_with_api_key(self, etl_processor):
        """Testa se o cliente HTTP está configurado com headers de autenticação."""
        # Verifica se o cliente tem headers configurados
        assert hasattr(etl_processor.client, "headers")

        # Se API_KEY estiver configurada, deve ter header de Authorization
        if etl_processor.api_key:
            assert "Authorization" in etl_processor.client.headers
            assert etl_processor.client.headers["Authorization"].startswith("Bearer ")
