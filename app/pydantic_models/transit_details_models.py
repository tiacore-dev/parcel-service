from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class TransitDetailsCreateSchema(BaseModel):
    transit_id: UUID
    parcel_id: UUID

    class Config:
        from_attributes = True


class TransitDetailsEditSchema(BaseModel):
    transit_id: Optional[UUID] = None
    parcel_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class TransitDetailsResponseSchema(BaseModel):
    details_id: UUID

    class Config:
        from_attributes = True


class TransitDetailsSchema(BaseModel):
    id: UUID = Field(..., alias="details_id")
    transit_id: UUID
    parcel_id: UUID

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    parcel_name: Optional[str] = Field(None)
    places_count: Optional[int] = Field(None)
    recipient_city: Optional[UUID] = Field(None)
    volume: Optional[float] = Field(None)
    weight: Optional[float] = Field(None)
    recipient_additional_info: Optional[str] = Field(None)

    class Config:
        from_attributes = True
        populate_by_name = True


class TransitDetailsListResponseSchema(BaseModel):
    total: int
    details: List[TransitDetailsSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def transit_details_filter_params(
    parcel_name: Optional[str] = Query(None, description="Фильтр по номеру накладной"),
    transit_id: Optional[UUID] = Query(None, description="Фильтр по ID транзита"),
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    sort_by: Literal["created_at"] = Query("created_at", description="Поле для сортировки"),
    order: Literal["asc", "desc"] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_name": parcel_name,
        "transit_id": transit_id,
        "parcel_id": parcel_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
