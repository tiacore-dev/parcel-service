from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class ParcelCargoCreateSchema(BaseModel):
    parcel_id: UUID
    weight: Decimal = Field(..., ge=0.01)
    length: Decimal = Field(..., ge=0.01)
    height: Decimal = Field(..., ge=0.01)
    quantity: int = Field(..., gt=0)
    cargo_type: str = Field(..., max_length=100)
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class ParcelCargoEditSchema(BaseModel):
    weight: Optional[Decimal] = Field(None, ge=0.01)
    length: Optional[Decimal] = Field(None, ge=0.01)
    height: Optional[Decimal] = Field(None, ge=0.01)
    quantity: Optional[int] = Field(None, gt=0)
    cargo_type: Optional[str] = Field(None, max_length=100)
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class ParcelCargoResponseSchema(BaseModel):
    cargo_id: UUID

    class Config:
        from_attributes = True


class ParcelCargoSchema(BaseModel):
    id: UUID = Field(..., alias="cargo_id")
    parcel_id: UUID
    weight: Decimal
    length: Decimal
    height: Decimal
    volume: Decimal
    quantity: int
    cargo_type: str
    total_weight: Decimal
    total_volume: Decimal
    comment: Optional[str] = None

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
    cargo_type: Optional[str] = Query(None, description="Тип груза"),
    sort_by: Optional[str] = Query("cargo_type", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_id": parcel_id,
        "cargo_type": cargo_type,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
