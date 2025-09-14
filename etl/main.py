from datetime import datetime
from typing import Any, Dict

import httpx
import pandas as pd

from db import SessionLocal
from models.data import Data as DataModel
from services import DataService, SignalService
from settings import API_BASE_URL, API_KEY, get_logger, setup_logging

# Configuração de logging
setup_logging()
logger = get_logger(__name__)


class DataETL:
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.api_key = API_KEY

        # Configuração do cliente HTTP com autenticação
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            # Alternativa comum: headers["X-API-Key"] = self.api_key
            # Ou: headers["api-key"] = self.api_key

        self.client = httpx.Client(timeout=30.0, headers=headers)
        self.signal_service = SignalService()
        self.data_service = DataService()

    def _get_signals_map(self, session: SessionLocal) -> Dict[str, int]:
        return self.signal_service.get_signals_map(session)

    def extract_available_fields(self) -> Dict[str, Any]:
        """
        Busca os campos (sinais) disponíveis no endpoint /fields.
        """
        if not self.api_key:
            logger.error("API_KEY não configurada. Verifique o arquivo .env")
            return {}

        try:
            response = self.client.get(f"{self.api_base_url}/fields")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Erro de autenticação: API_KEY inválida ou expirada")
            elif e.response.status_code == 403:
                logger.error("Acesso negado: verifique as permissões da API_KEY")
            else:
                logger.error(
                    f"Erro HTTP {e.response.status_code} ao buscar campos da API: {e}"
                )
            return {}
        except httpx.RequestError as e:
            logger.error(f"Não foi possível conectar à API: {e}")
            return {}

    def extract_data(
        self,
        start_ts: datetime,
        end_ts: datetime,
        fields: list[str],
        page_size: int = 25,
    ) -> Dict[str, Any]:
        """
        Busca dados de vento e potência para uma data específica.
        """
        if not self.api_key:
            logger.error("API_KEY não configurada. Verifique o arquivo .env")
            return []

        start_ts = datetime(
            start_ts.year, start_ts.month, start_ts.day, 0, 0, 0
        ).isoformat()

        end_ts = datetime(end_ts.year, end_ts.month, end_ts.day, 0, 0, 0).isoformat()

        fields_str = ",".join(fields)

        extracted_data = []

        params = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "fields": fields_str,
            "page": 1,
            "page_size": page_size,
        }

        try:
            response = self.client.get(f"{self.api_base_url}", params=params)
            response.raise_for_status()
            json_response = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Erro de autenticação: API_KEY inválida ou expirada")
            elif e.response.status_code == 403:
                logger.error("Acesso negado: verifique as permissões da API_KEY")
            else:
                logger.error(
                    f"Erro HTTP {e.response.status_code} ao buscar dados na página 1: {e}"
                )
            return []
        except httpx.RequestError as e:
            logger.error(f"Falha ao conectar à API na página 1: {e}")
            return []

        extracted_data.extend(json_response.get("data", []))

        total_pages = json_response.get("paging", {}).get("total_pages", 1)

        if total_pages > 1:
            for page in range(2, total_pages + 1):
                try:
                    params["page"] = page
                    response = self.client.get(f"{self.api_base_url}", params=params)
                    response.raise_for_status()
                    json_response = response.json()
                    extracted_data.extend(json_response.get("data", []))
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 401:
                        logger.error(
                            "Erro de autenticação: API_KEY inválida ou expirada"
                        )
                    elif e.response.status_code == 403:
                        logger.error(
                            "Acesso negado: verifique as permissões da API_KEY"
                        )
                    else:
                        logger.error(
                            f"Erro HTTP {e.response.status_code} ao buscar dados na página {page}: {e}"
                        )
                    return []
                except httpx.RequestError as e:
                    logger.error(f"Falha ao conectar à API na página {page}: {e}")
                    return []

        return extracted_data

    def transform_data(self, raw_data: list[dict]) -> pd.DataFrame:
        if not raw_data:
            logger.warning("Nenhum dado bruto para processar")
            return pd.DataFrame()

        logger.info("Processando e agregando dados com pandas")
        df = pd.DataFrame(raw_data)
        df["ts"] = pd.to_datetime(df["ts"])
        df.set_index("ts", inplace=True)

        transformed_data = df.resample("10min", closed="right").agg(
            ["mean", "min", "max", "std"]
        )
        transformed_data.columns = [
            "_".join(col).strip() for col in transformed_data.columns.values
        ]
        transformed_data.reset_index(inplace=True)

        logger.info(
            f"Agregação concluída: {len(transformed_data)} intervalos de 10 minutos"
        )
        return transformed_data

    def load_data(self, session: SessionLocal, transformed_data: pd.DataFrame):
        if transformed_data.empty:
            logger.warning("Nenhum dado agregado para salvar")
            return

        logger.info("Iniciando gravação dos dados no banco")
        signal_names = [col for col in transformed_data.columns if col != "ts"]
        signal_map = self._get_signals_map(session)
        data_points_to_add = []

        for _, row in transformed_data.iterrows():
            timestamp = row["ts"]
            for signal_name in signal_names:
                value = row[signal_name]
                if pd.notna(value):
                    data_points_to_add.append(
                        DataModel(
                            signal_id=signal_map[signal_name], ts=timestamp, value=value
                        )
                    )

        success = self.data_service.bulk_insert_data_points(session, data_points_to_add)
        if success:
            logger.info(f"{len(data_points_to_add)} pontos de dados salvos no banco")
        else:
            logger.error("Falha ao salvar os dados")


def main():
    """
    Orquestra todo o processo de ETL.
    """
    import argparse

    parser = argparse.ArgumentParser(description="ETL para dados de vento")

    parser.add_argument(
        "--start-ts",
        type=str,
        required=True,
        help="Data/hora de início (formato: YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)",
    )

    parser.add_argument(
        "--end-ts",
        type=str,
        required=True,
        help="Data/hora de fim (formato: YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)",
    )

    parser.add_argument(
        "--fields",
        type=str,
        default="wind_speed,power,ambient_temperature",
        help="Campos para extrair separados por vírgula (padrão: wind_speed,power,ambient_temperature)",
    )

    parser.add_argument(
        "--page-size",
        type=int,
        default=25,
        help="Tamanho da página para paginação (padrão: 25)",
    )

    args = parser.parse_args()

    try:
        start_ts = datetime.strptime(args.start_ts, "%Y-%m-%d")
        end_ts = datetime.strptime(args.end_ts, "%Y-%m-%d")

    except ValueError as e:
        logger.error(
            f"Formato de data inválido. Use YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS: {e}"
        )
        return

    try:
        etl_processor = DataETL()
        session = SessionLocal()
        logger.info(f"Iniciando ETL - Período: {start_ts.date()} até {end_ts.date()}")
        logger.info(f"Campos solicitados: {args.fields}")

        raw_data = etl_processor.extract_data(
            start_ts=start_ts,
            end_ts=end_ts,
            fields=args.fields.split(","),
            page_size=args.page_size,
        )

        logger.info(f"Dados extraídos: {len(raw_data)} registros")

        if raw_data:
            logger.debug(f"Primeiros registros: {raw_data[:3]}")

        transformed_data = etl_processor.transform_data(raw_data)

        if not transformed_data.empty:
            logger.debug(f"Dados transformados: {transformed_data.head()}")

        etl_processor.load_data(session, transformed_data)

    except Exception as e:

        logger.error(f"Erro durante execução do ETL: {e}")
        session.rollback()
        return

    finally:
        session.close()


if __name__ == "__main__":
    main()
