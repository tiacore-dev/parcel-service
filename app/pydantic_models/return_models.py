from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class ReturnToSenderCreateSchema(BaseModel):
    warehouse_id: UUID
    employee_id: UUID
    date: datetime
    parcel_id: UUID
    sender_name: str = Field(..., max_length=255)

    class Config:
        from_attributes = True


class ReturnToSenderEditSchema(BaseModel):
    warehouse_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    date: Optional[datetime] = None
    parcel_id: Optional[UUID] = None
    sender_name: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True


class ReturnToSenderResponseSchema(BaseModel):
    return_id: UUID

    class Config:
        from_attributes = True


class ReturnToSenderSchema(BaseModel):
    id: UUID = Field(..., alias="return_id")
    warehouse_id: UUID
    employee_id: UUID
    date: datetime
    parcel_id: UUID
    sender_name: str
    parcel_name: Optional[str] = Field(None)

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class ReturnToSenderListResponseSchema(BaseModel):
    total: int
    returns: List[ReturnToSenderSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def return_to_sender_filter_params(
    parcel_name: Optional[str] = Query(None, description="Фильтр по номеру накладной"),
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    warehouse_id: Optional[UUID] = Query(None, description="Фильтр по ID склада"),
    employee_id: Optional[UUID] = Query(None, description="Фильтр по ID сотрудника"),
    date_from: Optional[datetime] = Query(None, description="Дата от (включительно)"),
    date_to: Optional[datetime] = Query(None, description="Дата до (включительно)"),
    sender_name: Optional[str] = Query(None, description="Фильтр по имени отправителя"),
    sort_by: Optional[str] = Query("date", description="Поле для сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
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
