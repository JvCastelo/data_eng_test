import math
from datetime import datetime
from typing import List, Optional, Tuple

from dtos.data import DataResponseSchema, DataSchema, PagingSchema
from mappers.data import to_dto
from models.data import Data as DataModel
from sqlalchemy import func
from sqlalchemy.orm import Session


class DataService:

    def __init__(self, db: Session):
        self.db = db

    def get_available_fields(self) -> List[str]:
        return list(DataSchema.model_fields.keys())

    def get_data_with_pagination(
        self,
        start_ts: Optional[datetime] = None,
        end_ts: Optional[datetime] = None,
        fields: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> DataResponseSchema:

        base_query = self._build_base_query(fields)

        base_query = self._apply_date_filters(base_query, start_ts, end_ts)

        total_items = base_query.with_entities(func.count(DataModel.id)).scalar()
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
        has_next = page < total_pages

        offset = (page - 1) * page_size
        results = (
            base_query.order_by(DataModel.ts.desc())
            .offset(offset)
            .limit(page_size)
            .all()
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

    def _build_base_query(self, fields: Optional[str] = None):

        if fields:
            selected_field_names = set(field.strip() for field in fields.split(","))
            selected_field_names = self._ensure_required_fields(selected_field_names)
            selectable_columns = [
                getattr(DataModel, field) for field in selected_field_names
            ]
            return self.db.query(*selectable_columns)
        else:
            return self.db.query(DataModel)

    def _apply_date_filters(
        self, query, start_ts: Optional[datetime], end_ts: Optional[datetime]
    ):

        if start_ts:
            query = query.filter(DataModel.ts > start_ts)
        if end_ts:
            query = query.filter(DataModel.ts <= end_ts)
        return query

    def _ensure_required_fields(
        self, selected_fields: set[str], required_fields: list[str] = None
    ) -> set[str]:

        if required_fields is None:
            required_fields = ["ts"]
        return selected_fields.union(required_fields)
