import math
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, class_mapper

from db import SessionLocal
from dtos.data import DataResponseSchema, PagingSchema
from models.data import Data as DataModel

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


AVAILABLE_COLUMNS = {c.key: c for c in class_mapper(DataModel).columns}


@router.get("/fields", response_model=List[str], summary="Get available fields")
def get_available_fields(db: Session = Depends(get_db)):
    return list(AVAILABLE_COLUMNS.keys())


@router.get("/", response_model=DataResponseSchema, summary="Get data with pagination")
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
        selected_field_names = set(fields.strip() for field in fields.split(","))
        invalid_fields = selected_field_names - set(AVAILABLE_COLUMNS.keys())
        if invalid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Campos inválidos: {', '.join(invalid_fields)}",
            )
        selected_field_names.add("ts")
        selectable_columns = [
            AVAILABLE_COLUMNS[field] for field in selected_field_names
        ]
    else:
        selectable_columns = [
            AVAILABLE_COLUMNS[field] for field in AVAILABLE_COLUMNS.keys()
        ]

    base_query = db.query(*selectable_columns)

    if start_ts:
        base_query = base_query.filter(DataModel.ts >= start_ts)
    if end_ts:
        base_query = base_query.filter(DataModel.ts <= end_ts)

    total_items = base_query.with_entities(func.count(DataModel.id)).scalar()
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    has_next = page < total_pages

    offset = (page - 1) * page_size
    results = (
        base_query.order_by(DataModel.ts.desc()).offset(offset).limit(page_size).all()
    )
    data = [row._mapping for row in results]

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
