import re
from datetime import date, time
from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from zoneinfo import available_timezones

from fastapi import Query
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.database.models import DeliveryType, ParcelStatusEnum

IANA_TIMEZONES = available_timezones()
PHONE_REGEX = re.compile(r"^\+\d{8,15}$")
TELEGRAM_REGEX = re.compile(r"^@[\w\d_]{5,32}$")


class ParcelCreateSchema(BaseModel):
    name: Optional[str] = Field(None, alias="parcel_name")
    company_id: UUID
    # Отправитель
    sender_city: UUID
    sender_timezone: Optional[str] = Field(None, max_length=50)
    sender_address: str = Field(..., max_length=255)
    sender_warehouse: Optional[UUID] = Field(None)
    sender_delivery_type: DeliveryType
    sender_personal_data: Optional[UUID] = Field(None)
    sender_company: str = Field(..., max_length=255)
    sender_phone: str = Field(..., max_length=20)
    sender_email: Optional[EmailStr] = Field(None, max_length=100)
    sender_telegram: Optional[str] = Field(None, max_length=100)
    sender_coordinates_latitude: Optional[Decimal] = Field(None)
    sender_coordinates_longitude: Optional[Decimal] = Field(None)
    pickup_estimated_date: date
    pickup_time_from: time
    pickup_time_to: time
    sender_additional_info: Optional[str] = None

    # Получатель
    recipient_city: UUID
    recipient_timezone: Optional[str] = Field(None, max_length=50)
    recipient_address: str = Field(..., max_length=255)
    recipient_warehouse: Optional[UUID] = Field(None)
    recipient_delivery_type: DeliveryType
    recipient_personal_data: Optional[UUID] = Field(None)
    recipient_company: str = Field(..., max_length=255)
    recipient_phone: str = Field(..., max_length=20)
    recipient_email: Optional[EmailStr] = Field(None, max_length=100)
    recipient_telegram: Optional[str] = Field(None, max_length=100)
    recipient_coordinates_latitude: Optional[Decimal] = Field(None)
    recipient_coordinates_longitude: Optional[Decimal] = Field(None)
    delivery_estimated_date: date
    delivery_time_from: time
    delivery_time_to: time
    recipient_additional_info: Optional[str] = None

    # Общая информация
    note: Optional[str] = None
    weight: Decimal = Field(Decimal(0.0))
    volume: Decimal = Field(Decimal(0.0))
    places_count: int = Field(0)

    # Кастомная валидация для телефона
    @field_validator("sender_phone", "recipient_phone")
    def validate_phone(cls, v):
        if not PHONE_REGEX.match(v):
            raise ValueError("Телефон должен быть в формате +79999999999")
        return v

    # Кастомная валидация для Telegram
    @field_validator("sender_telegram", "recipient_telegram")
    def validate_telegram(cls, v):
        if v is not None and not TELEGRAM_REGEX.match(v):
            raise ValueError("Телеграм должен быть в формате @username (латиница, цифры, _)")
        return v

    @field_validator("sender_timezone", "recipient_timezone")
    def validate_timezone(cls, v):
        if v not in IANA_TIMEZONES:
            raise ValueError(f"Некорректная таймзона: {v}")
        return v

    @field_validator("pickup_time_to")
    def validate_pickup_time_range(cls, to_val, info):
        data = info.data
        from_val = data.get("pickup_time_from")
        if from_val and to_val <= from_val:
            raise ValueError("pickup_time_to должно быть позже pickup_time_from")
        return to_val

    @field_validator("delivery_time_to")
    def validate_delivery_time_range(cls, to_val, info):
        data = info.data
        from_val = data.get("delivery_time_from")
        if from_val and to_val <= from_val:
            raise ValueError("delivery_time_to должно быть позже delivery_time_from")
        return to_val

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ParcelEditSchema(BaseModel):
    name: Optional[str] = Field(None, alias="parcel_name")
    company_id: Optional[UUID] = Field(None)
    # Всё опционально для PATCH/UPDATE
    sender_city: Optional[UUID] = None
    sender_timezone: Optional[str] = Field(None, max_length=50)
    sender_address: Optional[str] = Field(None, max_length=255)
    sender_warehouse: Optional[UUID] = None
    sender_delivery_type: Optional[DeliveryType] = Field(None)
    sender_personal_data: Optional[UUID] = None
    sender_company: Optional[str] = Field(None, max_length=255)
    sender_phone: Optional[str] = Field(None, max_length=20)
    sender_email: Optional[EmailStr] = Field(None, max_length=100)
    sender_telegram: Optional[str] = Field(None, max_length=100)
    sender_coordinates_latitude: Optional[Decimal] = None
    sender_coordinates_longitude: Optional[Decimal] = None
    pickup_estimated_date: Optional[date] = None
    pickup_time_from: Optional[time] = None
    pickup_time_to: Optional[time] = None
    sender_additional_info: Optional[str] = None

    recipient_city: Optional[UUID] = None
    recipient_timezone: Optional[str] = Field(None, max_length=50)
    recipient_address: Optional[str] = Field(None, max_length=255)
    recipient_warehouse: Optional[UUID] = None
    recipient_delivery_type: Optional[DeliveryType] = Field(None)
    recipient_personal_data: Optional[UUID] = None
    recipient_company: Optional[str] = Field(None, max_length=255)
    recipient_phone: Optional[str] = Field(None, max_length=20)
    recipient_email: Optional[EmailStr] = Field(None, max_length=100)
    recipient_telegram: Optional[str] = Field(None, max_length=100)
    recipient_coordinates_latitude: Optional[Decimal] = None
    recipient_coordinates_longitude: Optional[Decimal] = None
    delivery_estimated_date: Optional[date] = None
    delivery_time_from: Optional[time] = None
    delivery_time_to: Optional[time] = None
    recipient_additional_info: Optional[str] = None

    note: Optional[str] = None
    weight: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    places_count: Optional[int] = None

    # Кастомная валидация для телефона
    @field_validator("sender_phone", "recipient_phone")
    def validate_phone(cls, v):
        if not PHONE_REGEX.match(v):
            raise ValueError("Телефон должен быть в формате +79999999999")
        return v

    # Кастомная валидация для Telegram
    @field_validator("sender_telegram", "recipient_telegram")
    def validate_telegram(cls, v):
        if v is not None and not TELEGRAM_REGEX.match(v):
            raise ValueError("Телеграм должен быть в формате @username (латиница, цифры, _)")
        return v

    @field_validator("sender_timezone", "recipient_timezone")
    def validate_timezone(cls, v):
        if v not in IANA_TIMEZONES:
            raise ValueError(f"Некорректная таймзона: {v}")
        return v

    @field_validator("pickup_time_to")
    def validate_pickup_time_range(cls, to_val, info):
        data = info.data
        from_val = data.get("pickup_time_from")
        if from_val and to_val <= from_val:
            raise ValueError("pickup_time_to должно быть позже pickup_time_from")
        return to_val

    @field_validator("delivery_time_to")
    def validate_delivery_time_range(cls, to_val, info):
        data = info.data
        from_val = data.get("delivery_time_from")
        if from_val and to_val <= from_val:
            raise ValueError("delivery_time_to должно быть позже delivery_time_from")
        return to_val

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ParcelResponseSchema(BaseModel):
    parcel_id: UUID

    class Config:
        from_attributes = True


class ParcelSchema(BaseModel):
    id: UUID = Field(..., alias="parcel_id")
    name: str = Field(..., alias="parcel_name")
    company_id: UUID = Field(...)

    # Отправитель
    sender_city: UUID
    sender_timezone: Optional[str] = Field(None, max_length=50)
    sender_address: str
    sender_warehouse: Optional[UUID] = Field(None)
    sender_delivery_type: DeliveryType
    sender_personal_data: Optional[UUID] = Field(None)
    sender_company: str
    sender_phone: str
    sender_email: Optional[EmailStr] = Field(None, max_length=100)
    sender_telegram: Optional[str] = Field(None, max_length=100)
    sender_coordinates_latitude: Optional[Decimal] = None
    sender_coordinates_longitude: Optional[Decimal] = None
    pickup_estimated_date: date
    pickup_time_from: time
    pickup_time_to: time
    sender_additional_info: Optional[str] = None

    # Получатель
    recipient_city: UUID
    recipient_timezone: Optional[str] = Field(None, max_length=50)
    recipient_address: str
    recipient_warehouse: Optional[UUID] = Field(None)
    recipient_delivery_type: DeliveryType
    recipient_personal_data: Optional[UUID] = Field(None)
    recipient_company: str
    recipient_phone: str
    recipient_email: Optional[EmailStr] = Field(None, max_length=100)
    recipient_telegram: Optional[str] = Field(None, max_length=100)
    recipient_coordinates_latitude: Optional[Decimal] = None
    recipient_coordinates_longitude: Optional[Decimal] = None
    delivery_estimated_date: date
    delivery_time_from: time
    delivery_time_to: time
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


class ParcelCurrentStatusSchema(BaseModel):
    parcel_id: UUID
    document_id: UUID
    document_type: str
    status: ParcelStatusEnum
    value: Optional[UUID] = Field(None)
    value_type: Optional[str] = Field(None)
    comment: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


def parcel_filter_params(
    company_id: Optional[UUID] = Query(None, description="ID компании"),
    parcel_name: Optional[str] = Query(None, description="Номер накладной"),
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
    sender_company: Optional[str] = Query(None, description="Частичный поиск по компании отправителя"),
    recipient_company: Optional[str] = Query(None, description="Частичный поиск по компании получателя"),
    search: Optional[str] = Query(
        None,
        description="Поиск по адресу или названию компаний (отправителя/получателя)",
    ),
    sort_by: Optional[str] = Query("pickup_estimated_date", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "company_id": company_id,
        "parcel_name": parcel_name,
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
