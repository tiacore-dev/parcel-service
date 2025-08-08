from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class ArrivalDetailsCreateSchema(BaseModel):
    arrival_id: UUID
    parcel_id: UUID

    class Config:
        from_attributes = True


class ArrivalDetailsEditSchema(BaseModel):
    arrival_id: Optional[UUID] = None
    parcel_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class ArrivalDetailsResponseSchema(BaseModel):
    details_id: UUID

    class Config:
        from_attributes = True


class ArrivalDetailsSchema(BaseModel):
    id: UUID = Field(..., alias="details_id")
    arrival_id: UUID
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


class ArrivalDetailsListResponseSchema(BaseModel):
    total: int
    details: List[ArrivalDetailsSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def arrival_details_filter_params(
    parcel_name: Optional[str] = Query(None, description="Фильтр по номеру накладной"),
    arrival_id: Optional[UUID] = Query(None, description="Фильтр по ID транзита"),
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    sort_by: Literal["created_at"] = Query("created_at", description="Поле для сортировки"),
    order: Literal["asc", "desc"] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_name": parcel_name,
        "arrival_id": arrival_id,
        "parcel_id": parcel_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
