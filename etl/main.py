from datetime import datetime
from typing import Any, Dict

import httpx
import pandas as pd

from etl.settings import API_BASE_URL


class DataETL:
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.client = httpx.Client(timeout=30.0)

    def extract_available_fields(self) -> Dict[str, Any]:
        """
        Busca os campos (sinais) disponíveis no endpoint /fields.
        """
        try:
            response = self.client.get(f"{self.api_base_url}/fields")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"ERRO: Não foi possível buscar os campos da API. Erro: {e}")
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
        except httpx.RequestError as e:
            print(f"ERRO: Falha ao conectar à API na página 1: {e}")
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
                except httpx.RequestError as e:
                    print(f"ERRO: Falha ao conectar à API na página {page}: {e}")
                    return []

        return extracted_data

    def transform_data(self, raw_data: list[dict]) -> pd.DataFrame:
        if not raw_data:
            print("AVISO: Nenhum dado bruto para processar.")
            return pd.DataFrame()
        print("INFO: Processando e agregando dados com pandas...")
        df = pd.DataFrame(raw_data)
        df["ts"] = pd.to_datetime(df["ts"])
        df.set_index("ts", inplace=True)
        transformed_data = df.resample("10T", closed="right").agg(
            ["mean", "min", "max", "std"]
        )
        transformed_data.columns = [
            "_".join(col).strip() for col in transformed_data.columns.values
        ]
        transformed_data.reset_index(inplace=True)
        print("INFO: Agregação concluída.")
        return transformed_data


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
        print(f"ERRO: Formato de data inválido. Use YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS")
        print(f"Erro: {e}")
        return

    try:
        etl_processor = DataETL()

        print(f"Extraindo dados de {start_ts} até {end_ts}")
        print(f"Campos: {args.fields}")

        raw_data = etl_processor.extract_data(
            start_ts=start_ts,
            end_ts=end_ts,
            fields=args.fields.split(","),
            page_size=args.page_size,
        )

        print(f"Dados extraídos: {len(raw_data)} registros")
        print(raw_data)

        transformed_data = etl_processor.transform_data(raw_data)
        print(transformed_data)

        # 3. Carga (Load)
        # save_data_to_db(session, transformed_data)

    except Exception as e:
        print(f"ERRO durante execução do ETL: {e}")
        return


if __name__ == "__main__":
    main()
