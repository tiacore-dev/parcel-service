from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class ParcelCreateSchema(BaseModel):
    # Отправитель
    sender_city: UUID
    sender_address: str = Field(..., max_length=255)
    sender_warehouse: UUID
    sender_personal_data: UUID
    sender_company: str = Field(..., max_length=255)
    sender_phone: str = Field(..., max_length=20)
    sender_email: str = Field(..., max_length=100)
    sender_telegram: str = Field(..., max_length=100)
    sender_coordinates_latitude: Decimal
    sender_coordinates_longitude: Decimal
    pickup_estimated_date: date
    pickup_time_from: datetime
    pickup_time_to: datetime
    sender_additional_info: Optional[str] = None

    # Получатель
    recipient_city: UUID
    recipient_address: str = Field(..., max_length=255)
    recipient_warehouse: UUID
    recipient_personal_data: UUID
    recipient_company: str = Field(..., max_length=255)
    recipient_phone: str = Field(..., max_length=20)
    recipient_email: str = Field(..., max_length=100)
    recipient_telegram: str = Field(..., max_length=100)
    recipient_coordinates_latitude: Decimal
    recipient_coordinates_longitude: Decimal
    delivery_estimated_date: date
    delivery_time_from: datetime
    delivery_time_to: datetime
    recipient_additional_info: Optional[str] = None

    # Общая информация
    note: Optional[str] = None
    weight: Decimal
    volume: Decimal
    places_count: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ParcelEditSchema(BaseModel):
    # Всё опционально для PATCH/UPDATE
    sender_city: Optional[UUID] = None
    sender_address: Optional[str] = Field(None, max_length=255)
    sender_warehouse: Optional[UUID] = None
    sender_personal_data: Optional[UUID] = None
    sender_company: Optional[str] = Field(None, max_length=255)
    sender_phone: Optional[str] = Field(None, max_length=20)
    sender_email: Optional[str] = Field(None, max_length=100)
    sender_telegram: Optional[str] = Field(None, max_length=100)
    sender_coordinates_latitude: Optional[Decimal] = None
    sender_coordinates_longitude: Optional[Decimal] = None
    pickup_estimated_date: Optional[date] = None
    pickup_time_from: Optional[datetime] = None
    pickup_time_to: Optional[datetime] = None
    sender_additional_info: Optional[str] = None

    recipient_city: Optional[UUID] = None
    recipient_address: Optional[str] = Field(None, max_length=255)
    recipient_warehouse: Optional[UUID] = None
    recipient_personal_data: Optional[UUID] = None
    recipient_company: Optional[str] = Field(None, max_length=255)
    recipient_phone: Optional[str] = Field(None, max_length=20)
    recipient_email: Optional[str] = Field(None, max_length=100)
    recipient_telegram: Optional[str] = Field(None, max_length=100)
    recipient_coordinates_latitude: Optional[Decimal] = None
    recipient_coordinates_longitude: Optional[Decimal] = None
    delivery_estimated_date: Optional[date] = None
    delivery_time_from: Optional[datetime] = None
    delivery_time_to: Optional[datetime] = None
    recipient_additional_info: Optional[str] = None

    note: Optional[str] = None
    weight: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    places_count: Optional[int] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ParcelResponseSchema(BaseModel):
    parcel_id: UUID

    class Config:
        from_attributes = True


class ParcelSchema(BaseModel):
    id: UUID = Field(..., alias="parcel_id")

    # Отправитель
    sender_city: UUID
    sender_address: str
    sender_warehouse: UUID
    sender_personal_data: UUID
    sender_company: str
    sender_phone: str
    sender_email: str
    sender_telegram: str
    sender_coordinates_latitude: Decimal
    sender_coordinates_longitude: Decimal
    pickup_estimated_date: date
    pickup_time_from: datetime
    pickup_time_to: datetime
    sender_additional_info: Optional[str] = None

    # Получатель
    recipient_city: UUID
    recipient_address: str
    recipient_warehouse: UUID
    recipient_personal_data: UUID
    recipient_company: str
    recipient_phone: str
    recipient_email: str
    recipient_telegram: str
    recipient_coordinates_latitude: Decimal
    recipient_coordinates_longitude: Decimal
    delivery_estimated_date: date
    delivery_time_from: datetime
    delivery_time_to: datetime
    recipient_additional_info: Optional[str] = None

    # Общая информация
    note: Optional[str] = None
    weight: Decimal
    volume: Decimal
    places_count: int

    class Config:
        from_attributes = True
        populate_by_name = True


class ParcelListResponseSchema(BaseModel):
    total: int
    parcels: List[ParcelSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def parcel_filter_params(
    sender_city: Optional[UUID] = Query(None, description="Город отправителя"),
    recipient_city: Optional[UUID] = Query(None, description="Город получателя"),
    sender_warehouse: Optional[UUID] = Query(None, description="Склад отправителя"),
    recipient_warehouse: Optional[UUID] = Query(None, description="Склад получателя"),
    pickup_date_from: Optional[date] = Query(None, description="Дата забора с"),
    pickup_date_to: Optional[date] = Query(None, description="Дата забора по"),
    delivery_date_from: Optional[date] = Query(None, description="Дата доставки с"),
    delivery_date_to: Optional[date] = Query(None, description="Дата доставки по"),
    min_weight: Optional[float] = Query(None, description="Минимальный вес"),
    max_weight: Optional[float] = Query(None, description="Максимальный вес"),
    min_volume: Optional[float] = Query(None, description="Минимальный объем"),
    max_volume: Optional[float] = Query(None, description="Максимальный объем"),
    sender_company: Optional[str] = Query(
        None, description="Частичный поиск по компании отправителя"
    ),
    recipient_company: Optional[str] = Query(
        None, description="Частичный поиск по компании получателя"
    ),
    search: Optional[str] = Query(
        None,
        description="Поиск по адресу или названию компаний (отправителя/получателя)",
    ),
    sort_by: Optional[str] = Query(
        "pickup_estimated_date", description="Поле сортировки"
    ),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "sender_city": sender_city,
        "recipient_city": recipient_city,
        "sender_warehouse": sender_warehouse,
        "recipient_warehouse": recipient_warehouse,
        "pickup_date_from": pickup_date_from,
        "pickup_date_to": pickup_date_to,
        "delivery_date_from": delivery_date_from,
        "delivery_date_to": delivery_date_to,
        "min_weight": min_weight,
        "max_weight": max_weight,
        "min_volume": min_volume,
        "max_volume": max_volume,
        "sender_company": sender_company,
        "recipient_company": recipient_company,
        "search": search,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
