from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field

from app.pydantic_models.parcel_models import ParcelShortSchema


class ArrivalCreateSchema(BaseModel):
    warehouse_id: UUID
    date: datetime

    class Config:
        from_attributes = True


class ArrivalCreateBulkSchema(BaseModel):
    warehouse_id: UUID
    date: datetime
    parcels: List[UUID]

    class Config:
        from_attributes = True


class ArrivalEditSchema(BaseModel):
    warehouse_id: Optional[UUID] = None
    date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArrivalResponseSchema(BaseModel):
    arrival_id: UUID

    class Config:
        from_attributes = True


class ArrivalSchema(BaseModel):
    id: UUID = Field(..., alias="arrival_id")
    warehouse_id: UUID
    date: datetime
    parcel_count: Optional[str] = Field(None)
    parcels: Optional[List[ParcelShortSchema]] = Field(None)

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class ArrivalListResponseSchema(BaseModel):
    total: int
    arrivals: List[ArrivalSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def arrival_filter_params(
    parcel_name: Optional[str] = Query(None, description="Фильтр по номеру накладной"),
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    warehouse_id: Optional[UUID] = Query(None, description="Фильтр по ID склада"),
    date_from: Optional[datetime] = Query(None, description="Дата от (включительно)"),
    date_to: Optional[datetime] = Query(None, description="Дата до (включительно)"),
    sort_by: Optional[str] = Query("date", description="Поле для сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_name": parcel_name,
        "parcel_id": parcel_id,
        "warehouse_id": warehouse_id,
        "date_from": date_from,
        "date_to": date_to,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
