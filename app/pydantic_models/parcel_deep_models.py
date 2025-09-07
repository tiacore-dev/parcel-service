# --- pydantic_models/parcel_deep_models.py ---

from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field
from tiacore_lib.enums import ServiceType  # если у тебя ServiceType в models — поправь импорт

# reuse ParcelCreateSchema в качестве базы
from app.pydantic_models.parcel_models import ParcelCreateSchema


# ВНИМАНИЕ: inline-элементы без parcel_id — его подставим на бэке
class ParcelCargoInlineCreate(BaseModel):
    cargo_type_id: UUID
    weight: Decimal = Field(..., ge=0.01)
    length: Decimal = Field(..., ge=0.01)
    height: Decimal = Field(..., ge=0.01)
    width: Decimal = Field(..., ge=0.01)
    quantity: int = Field(..., gt=0)
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class ParcelProductInlineCreate(BaseModel):
    name: str
    price: Decimal = Field(..., ge=0.01)
    quantity: int = Field(..., ge=1)
    article_number: str
    delivered: Optional[bool] = False
    serial_number: str

    class Config:
        from_attributes = True


class ExtraServiceInlineCreate(BaseModel):
    # Доп. услуги сверх стандартной (например, упаковка, подъем, пр.)
    service_type: ServiceType
    base_value: float
    summ: Optional[float] = None
    price_id: Optional[UUID] = None
    contract_id: Optional[UUID] = None  # можно не указывать — возьмём основной

    class Config:
        from_attributes = True


class ParcelDeepCreateSchema(ParcelCreateSchema):
    cargo: List[ParcelCargoInlineCreate] = Field(default_factory=list)
    products: List[ParcelProductInlineCreate] = Field(default_factory=list)
    extra_services: List[ExtraServiceInlineCreate] = Field(default_factory=list)


class ParcelDeepCreateResponse(BaseModel):
    parcel_id: UUID
    cargo_ids: List[UUID]
    product_ids: List[UUID]
    service_ids: List[UUID]
