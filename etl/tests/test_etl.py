from datetime import datetime
from unittest.mock import Mock, patch

import httpx
import pandas as pd
import pytest
from main import DataETL
from models.data import Data, Signal


class TestETL:

    @pytest.fixture
    def etl_processor(self):
        return DataETL()

    @pytest.mark.unit
    def test_init(self, etl_processor):
        assert etl_processor.api_base_url is not None
        assert etl_processor.client is not None
        assert hasattr(etl_processor, "api_key")

    @pytest.mark.unit
    def test_transform_data_success(self, etl_processor, sample_raw_data):
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
        simple_df = sample_transformed_data[
            ["ts", "wind_speed_mean", "power_mean"]
        ].copy()

        etl_processor.load_data(test_session, simple_df)

        saved_data = test_session.query(Data).all()
        assert len(saved_data) > 0

    @pytest.mark.unit
    def test_extract_available_fields_no_api_key(self, etl_processor):
        with patch.object(etl_processor, "api_key", None):
            result = etl_processor.extract_available_fields()
            assert result == {}

    @pytest.mark.unit
    def test_extract_data_no_api_key(self, etl_processor):
        with patch.object(etl_processor, "api_key", None):
            result = etl_processor.extract_data(
                datetime(2024, 1, 1), datetime(2024, 1, 2), ["wind_speed"]
            )
            assert result == []

    @pytest.mark.unit
    def test_extract_available_fields_auth_error(self, etl_processor):
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
        assert hasattr(etl_processor.client, "headers")

        if etl_processor.api_key:
            assert "Authorization" in etl_processor.client.headers
            assert etl_processor.client.headers["Authorization"].startswith("Bearer ")
