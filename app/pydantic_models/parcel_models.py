import re
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import List, Literal, Optional
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
    delivery_estimated_date: Optional[date] = Field(None)
    delivery_time_from: Optional[time] = Field(None)
    delivery_time_to: Optional[time] = Field(None)
    recipient_additional_info: Optional[str] = None

    # Общая информация
    note: Optional[str] = None
    weight: Decimal = Field(Decimal(0.0))
    volume: Decimal = Field(Decimal(0.0))
    places_count: int = Field(0)

    contract_id: UUID = Field(...)

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


class ParcelShortSchema(BaseModel):
    parcel_name: Optional[str] = Field(None)
    places_count: Optional[int] = Field(None)
    recipient_city: Optional[UUID] = Field(None)
    volume: Optional[float] = Field(None)
    weight: Optional[float] = Field(None)
    recipient_additional_info: Optional[str] = Field(None)


class ParcelSchema(BaseModel):
    id: UUID = Field(..., alias="parcel_id")
    name: str = Field(..., alias="parcel_name")
    company_id: UUID = Field(...)

    # Отправитель
    sender_city: UUID

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
    delivery_estimated_date: Optional[date] = Field(None)
    delivery_time_from: Optional[time] = Field(None)
    delivery_time_to: Optional[time] = Field(None)
    recipient_additional_info: Optional[str] = Field(None)

    # Общая информация
    note: Optional[str] = None
    weight: float
    volume: float
    places_count: int

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    # status: Optional[ParcelStatusEnum] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class ParcelAllSchema(ParcelSchema):
    status: Optional[ParcelStatusEnum] = Field(None)


class ParcelCurrentStatusSchema(BaseModel):
    parcel_id: UUID
    document_id: UUID
    document_type: str
    status: ParcelStatusEnum
    value: Optional[UUID] = Field(None)
    value_type: Optional[str] = Field(None)
    date: datetime
    comment: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class ParcelViewSchema(ParcelSchema):
    status: Optional[ParcelCurrentStatusSchema] = None


class ParcelListResponseSchema(BaseModel):
    total: int
    parcels: List[ParcelAllSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


class ParcelSortFields(str, Enum):
    parcel_name = "name"
    sender_city = "sender_city"
    sender_address = "sender_address"
    sender_warehouse = "sender_warehouse"
    sender_delivery_type = "sender_delivery_type"
    sender_personal_data = "sender_personal_data"
    sender_company = "sender_company"
    sender_phone = "sender_phone"
    sender_email = "sender_email"
    sender_telegram = "sender_telegram"
    sender_coordinates_latitude = "sender_coordinates_latitude"
    sender_coordinates_longitude = "sender_coordinates_longitude"
    pickup_estimated_date = "pickup_estimated_date"
    pickup_time_from = "pickup_time_from"
    pickup_time_to = "pickup_time_to"
    sender_additional_info = "sender_additional_info"
    recipient_city = "recipient_city"
    recipient_address = "recipient_address"
    recipient_warehouse = "recipient_warehouse"
    recipient_delivery_type = "recipient_delivery_type"
    recipient_personal_data = "recipient_personal_data"
    recipient_company = "recipient_company"
    recipient_phone = "recipient_phone"
    recipient_email = "recipient_email"
    recipient_telegram = "recipient_telegram"
    recipient_coordinates_latitude = "recipient_coordinates_latitude"
    recipient_coordinates_longitude = "recipient_coordinates_longitude"
    delivery_estimated_date = "delivery_estimated_date"
    delivery_time_from = "delivery_time_from"
    delivery_time_to = "delivery_time_to"
    recipient_additional_info = "recipient_additional_info"
    note = "note"
    weight = "weight"
    volume = "volume"
    places_count = "places_count"
    created_at = "created_at"
    modified_at = "modified_at"


def parcel_filter_params(
    company_id: Optional[UUID] = Query(None, description="ID компании"),
    sender_city: Optional[UUID] = Query(None, description="Город отправителя"),
    recipient_city: Optional[UUID] = Query(None, description="Город получателя"),
    pickup_date_from: Optional[date] = Query(None, description="Дата забора с"),
    pickup_date_to: Optional[date] = Query(None, description="Дата забора по"),
    search: Optional[str] = Query(
        None,
        description="Поиск по адресу или названию компаний (отправителя/получателя)",
    ),
    sort_by: ParcelSortFields = Query(ParcelSortFields.created_at, description="Поле сортировки"),
    order: Literal["asc", "desc"] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1),
    page_size: Optional[int] = Query(10, ge=1, le=100),
):
    return {
        "company_id": company_id,
        "sender_city": sender_city,
        "recipient_city": recipient_city,
        "pickup_date_from": pickup_date_from,
        "pickup_date_to": pickup_date_to,
        "search": search,
        "sort_by": sort_by.value,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
