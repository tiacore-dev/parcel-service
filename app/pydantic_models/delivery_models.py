from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class DeliveryToRecipientCreateSchema(BaseModel):
    warehouse_id: UUID
    employee_id: UUID
    date: datetime
    parcel_id: UUID
    recipient_name: str = Field(..., max_length=255)

    class Config:
        from_attributes = True


class DeliveryToRecipientEditSchema(BaseModel):
    warehouse_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    date: Optional[datetime] = None
    parcel_id: Optional[UUID] = None
    recipient_name: Optional[str] = Field(None, max_length=255)

    class Config:
        from_attributes = True


class DeliveryToRecipientResponseSchema(BaseModel):
    delivery_id: UUID

    class Config:
        from_attributes = True


class DeliveryToRecipientSchema(BaseModel):
    id: UUID = Field(..., alias="delivery_id")
    warehouse_id: UUID
    employee_id: UUID
    date: datetime
    parcel_id: UUID
    recipient_name: str
    parcel_name: Optional[str] = Field(None)

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class DeliveryToRecipientListResponseSchema(BaseModel):
    total: int
    deliveries: List[DeliveryToRecipientSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def delivery_to_recipient_filter_params(
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    warehouse_id: Optional[UUID] = Query(None, description="Фильтр по ID склада"),
    employee_id: Optional[UUID] = Query(None, description="Фильтр по ID сотрудника"),
    date_from: Optional[datetime] = Query(None, description="Дата от (включительно)"),
    date_to: Optional[datetime] = Query(None, description="Дата до (включительно)"),
    recipient_name: Optional[str] = Query(None, description="Фильтр по имени получателя"),
    sort_by: Optional[str] = Query("date", description="Поле для сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_id": parcel_id,
        "warehouse_id": warehouse_id,
        "employee_id": employee_id,
        "date_from": date_from,
        "date_to": date_to,
        "recipient_name": recipient_name,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
