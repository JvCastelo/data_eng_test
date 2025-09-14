from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class DataSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    ts: datetime
    wind_speed: float | None = Field(default=None, description="Velocidade do vento")
    power: float | None = Field(default=None, description="Potência")
    ambient_temperature: float | None = Field(
        default=None, description="Temperatura ambiente"
    )


class PagingSchema(BaseModel):
    page: int = Field(description="Número da página atual")
    total_pages: int = Field(description="Número total de páginas disponíveis")
    items_per_page: int = Field(description="Número de itens por página")
    total_items: int = Field(description="Número total de itens disponíveis")
    has_next: bool = Field(description="Indica se há uma página posterior")


class DataResponseSchema(BaseModel):
    data: List[DataSchema]
    paging: PagingSchema
