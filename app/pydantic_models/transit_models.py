from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field

from app.database.models import TransitStatusEnum
from app.pydantic_models.parcel_models import ParcelShortSchema


class TransitCreateSchema(BaseModel):
    name: Optional[str] = Field(None, alias="transit_name", max_length=10)
    warehouse_from_id: UUID
    warehouse_to_id: UUID
    date: datetime
    status: TransitStatusEnum

    class Config:
        from_attributes = True


class TransitEditSchema(BaseModel):
    name: Optional[str] = Field(None, alias="transit_name")
    warehouse_from_id: Optional[UUID] = None
    warehouse_to_id: Optional[UUID] = None
    date: Optional[datetime] = None
    status: Optional[TransitStatusEnum] = None

    class Config:
        from_attributes = True


class TransitResponseSchema(BaseModel):
    transit_id: UUID

    class Config:
        from_attributes = True


class TransitSchema(BaseModel):
    id: UUID = Field(..., alias="transit_id")
    name: str = Field(..., alias="transit_name")
    warehouse_from_id: UUID
    warehouse_to_id: UUID
    date: datetime
    status: TransitStatusEnum
    parcel_count: Optional[int] = Field(None)
    parcels: Optional[List[ParcelShortSchema]] = Field(None)

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class TransitListResponseSchema(BaseModel):
    total: int
    transits: List[TransitSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def transit_filter_params(
    transit_name: Optional[str] = Query(None),
    status: Optional[TransitStatusEnum] = Query(None, description="Фильтр по статусу транзита"),
    warehouse_from_id: Optional[UUID] = Query(None, description="Фильтр по складу отправления"),
    warehouse_to_id: Optional[UUID] = Query(None, description="Фильтр по складу назначения"),
    date_from: Optional[datetime] = Query(None, description="Дата от (включительно)"),
    date_to: Optional[datetime] = Query(None, description="Дата до (включительно)"),
    sort_by: Optional[str] = Query("date", description="Поле для сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "transit_name": transit_name,
        "status": status,
        "warehouse_from_id": warehouse_from_id,
        "warehouse_to_id": warehouse_to_id,
        "date_from": date_from,
        "date_to": date_to,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
