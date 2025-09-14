import math
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, class_mapper

from api.db import SessionLocal
from api.dtos.data import DataResponseSchema, DataSchema, PagingSchema
from api.mappers.data import to_dto
from api.models.data import Data as DataModel

router = APIRouter(prefix="/api/v1/data", tags=["Data"])


def get_db():
    """
    Para cada requisição à API, ela cria uma nova sessão com o banco,
    disponibiliza essa sessão para a rota e garante que ela seja
    fechada ao final, mesmo que ocorra um erro.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_required_fields(
    selected_fields: set[str], required_fields: list[str] = None
) -> set[str]:
    """
    Garante que campos obrigatórios sejam sempre incluídos na consulta.

    Args:
        selected_fields: Campos selecionados pelo usuário
        required_fields: Campos obrigatórios (padrão: ["ts"])

    Returns:
        Conjunto de campos incluindo os obrigatórios
    """
    if required_fields is None:
        required_fields = ["ts"]

    return selected_fields.union(required_fields)


AVAILABLE_COLUMNS = list(DataSchema.model_fields.keys())


@router.get("/fields", response_model=List[str], summary="Get available fields")
def get_available_fields(db: Session = Depends(get_db)):
    return AVAILABLE_COLUMNS


@router.get(
    "/",
    response_model=DataResponseSchema,
    response_model_exclude_none=True,
    summary="Get data with pagination",
)
def get_data(
    start_ts: datetime | None = Query(None, description="Data de início"),
    end_ts: datetime | None = Query(None, description="Data de fim"),
    fields: str | None = Query(
        None,
        description="Campos desejados, separados por vírgula. Ex: wind_speed,power",
    ),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(25, ge=1, le=1000, description="Número de itens por página"),
    db: Session = Depends(get_db),
):
    if fields:
        selected_field_names = set(field.strip() for field in fields.split(","))
        invalid_fields = selected_field_names - set(AVAILABLE_COLUMNS)
        if invalid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Campos inválidos: {', '.join(invalid_fields)}",
            )
        selected_field_names = ensure_required_fields(selected_field_names)
        selectable_columns = [
            getattr(DataModel, field) for field in selected_field_names
        ]
        base_query = db.query(*selectable_columns)
    else:
        base_query = db.query(DataModel)

    if start_ts:
        base_query = base_query.filter(DataModel.ts > start_ts)
    if end_ts:
        base_query = base_query.filter(DataModel.ts <= end_ts)

    total_items = base_query.with_entities(func.count(DataModel.id)).scalar()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    has_next = page < total_pages

    offset = (page - 1) * page_size
    results = (
        base_query.order_by(DataModel.ts.desc()).offset(offset).limit(page_size).all()
    )
    data = [to_dto(row) for row in results]

    return DataResponseSchema(
        data=data,
        paging=PagingSchema(
            page=page,
            total_pages=total_pages,
            items_per_page=page_size,
            total_items=total_items,
            has_next=has_next,
        ),
    )
