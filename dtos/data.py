from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class DataSchemaBase(BaseModel):
    ts: datetime
    wind_speed: float | None = Field(default=None, description="Velocidade do vento")
    power: float | None = Field(default=None, description="Potência")
    ambient_temperature: float | None = Field(
        default=None, description="Temperatura ambiente"
    )


class DataSchemaCreate(DataSchemaBase):
    pass


class DataSchema(DataSchemaBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PagingSchema(BaseModel):
    page: int = Field(description="Número da página atual")
    total_pages: int = Field(description="Número total de páginas disponíveis")
    items_per_page: int = Field(description="Número de itens por página")
    total_items: int = Field(description="Número total de itens disponíveis")
    has_next: bool = Field(description="Indica se há uma página posterior")


class DataResponseSchema(BaseModel):
    data: List[Dict[str, Any]]
    paging: PagingSchema
