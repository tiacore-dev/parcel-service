from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field

from app.pydantic_models.parcel_models import ParcelShortSchema


class ReturnCreateSchema(BaseModel):
    warehouse_id: UUID
    employee_id: UUID
    date: datetime
    sender_name: str = Field(..., max_length=255)

    class Config:
        from_attributes = True


class ReturnCreateBulkSchema(BaseModel):
    warehouse_id: UUID
    employee_id: UUID
    date: datetime
    sender_name: str = Field(..., max_length=255)
    parcels: List[UUID]

    class Config:
        from_attributes = True


class ReturnEditSchema(BaseModel):
    warehouse_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    date: Optional[datetime] = None
    sender_name: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True


class ReturnResponseSchema(BaseModel):
    return_id: UUID

    class Config:
        from_attributes = True


class ReturnSchema(BaseModel):
    id: UUID = Field(..., alias="return_id")
    warehouse_id: UUID
    employee_id: UUID
    date: datetime
    sender_name: str = Field(..., max_length=255)
    parcel_count: Optional[int] = Field(None)
    parcels: Optional[List[ParcelShortSchema]] = Field(None)

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class ReturnListResponseSchema(BaseModel):
    total: int
    returns: List[ReturnSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def return_filter_params(
    parcel_name: Optional[str] = Query(None, description="Фильтр по номеру накладной"),
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    warehouse_id: Optional[UUID] = Query(None, description="Фильтр по ID склада"),
    employee_id: Optional[UUID] = Query(None, description="Фильтр по ID сотрудника"),
    date_from: Optional[datetime] = Query(None, description="Дата от (включительно)"),
    date_to: Optional[datetime] = Query(None, description="Дата до (включительно)"),
    sender_name: Optional[str] = Query(None, description="Фильтр по имени отправителя"),
    sort_by: Literal["date", "created_at"] = Query("date", description="Поле для сортировки"),
    order: Literal["asc", "desc"] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_name": parcel_name,
        "parcel_id": parcel_id,
        "warehouse_id": warehouse_id,
        "employee_id": employee_id,
        "date_from": date_from,
        "date_to": date_to,
        "sender_name": sender_name,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
