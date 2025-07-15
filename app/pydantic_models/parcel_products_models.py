from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class ParcelProductCreateSchema(BaseModel):
    parcel_id: UUID
    name: str
    price: Decimal = Field(..., ge=0.01, description="Цена должна быть больше 0")
    quantity: int = Field(..., ge=1, description="Количество должно быть минимум 1")
    article_number: str
    delivered: Optional[bool] = False
    serial_number: str

    class Config:
        from_attributes = True


class ParcelProductEditSchema(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0.01, description="Цена должна быть больше 0")
    quantity: Optional[int] = Field(None, ge=1, description="Количество должно быть минимум 1")
    article_number: Optional[str] = None
    delivered: Optional[bool] = None
    serial_number: Optional[str] = None

    class Config:
        from_attributes = True


class ParcelProductResponseSchema(BaseModel):
    product_id: UUID

    class Config:
        from_attributes = True


class ParcelProductSchema(BaseModel):
    id: UUID = Field(..., alias="product_id")
    parcel_id: UUID
    name: str
    price: Decimal
    quantity: int
    summ: Decimal
    article_number: str
    delivered: bool
    serial_number: str

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class ParcelProductListResponseSchema(BaseModel):
    total: int
    products: List[ParcelProductSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def parcel_product_filter_params(
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    article_number: Optional[str] = Query(None, description="Артикул"),
    delivered: Optional[bool] = Query(None, description="Статус доставки"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_id": parcel_id,
        "article_number": article_number,
        "delivered": delivered,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
