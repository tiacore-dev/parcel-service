from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field, field_validator


class ParcelCargoCreateSchema(BaseModel):
    parcel_id: UUID
    cargo_type_id: UUID
    weight: Decimal = Field(..., ge=0.01)
    length: Decimal = Field(..., ge=0.01)
    height: Decimal = Field(..., ge=0.01)
    width: Decimal = Field(..., ge=0.01)
    quantity: int = Field(..., gt=0)
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class ParcelCargoEditSchema(BaseModel):
    cargo_type_id: Optional[UUID] = Field(None)
    weight: Optional[Decimal] = Field(None, ge=0.01)
    length: Optional[Decimal] = Field(None, ge=0.01)
    height: Optional[Decimal] = Field(None, ge=0.01)
    width: Optional[Decimal] = Field(None, ge=0.01)
    quantity: Optional[int] = Field(None, gt=0)
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class ParcelCargoResponseSchema(BaseModel):
    cargo_id: UUID

    class Config:
        from_attributes = True


class ParcelCargoSchema(BaseModel):
    id: UUID = Field(..., alias="cargo_id")
    cargo_type: Optional[str] = None
    parcel_id: UUID
    weight: Decimal
    length: Decimal
    height: Decimal
    width: Decimal
    volume: float
    quantity: int
    total_weight: float
    total_volume: float
    comment: Optional[str] = None

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    @field_validator("cargo_type", mode="before")
    @classmethod
    def _extract_name(cls, v):
        # если уже строка — вернём как есть
        if isinstance(v, str) or v is None:
            return v
        # если это объект модели (prefetch_related загрузил его)
        name = getattr(v, "name", None)
        return name if name is not None else str(v)

    class Config:
        from_attributes = True
        populate_by_name = True


class ParcelCargoListResponseSchema(BaseModel):
    total: int
    cargo: List[ParcelCargoSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def parcel_cargo_filter_params(
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    cargo_type_id: Optional[UUID] = Query(None, description="Тип груза"),
    sort_by: Literal["created_at", "total_weight", "total_volume", "quantity"] = Query(
        "created_at", description="Поле сортировки"
    ),
    order: Literal["asc", "desc"] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_id": parcel_id,
        "cargo_type_id": cargo_type_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
