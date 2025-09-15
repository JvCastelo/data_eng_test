from datetime import datetime
from typing import List

from auth import get_current_user
from db import SessionLocal
from dtos.data import DataResponseSchema, DataSchema
from fastapi import APIRouter, Depends, HTTPException, Query
from services import DataService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/data", tags=["Data"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_data_service(db: Session = Depends(get_db)) -> DataService:
    return DataService(db)


@router.get("/fields", response_model=List[str], summary="Get available fields")
def get_available_fields(
    data_service: DataService = Depends(get_data_service),
    current_user: dict = Depends(get_current_user),
):
    return data_service.get_available_fields()


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
    data_service: DataService = Depends(get_data_service),
    current_user: dict = Depends(get_current_user),
):
    if fields:
        available_fields = data_service.get_available_fields()
        selected_field_names = set(field.strip() for field in fields.split(","))
        invalid_fields = selected_field_names - set(available_fields)
        if invalid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Campos inválidos: {', '.join(invalid_fields)}",
            )

    return data_service.get_data_with_pagination(
        start_ts=start_ts,
        end_ts=end_ts,
        fields=fields,
        page=page,
        page_size=page_size,
    )
