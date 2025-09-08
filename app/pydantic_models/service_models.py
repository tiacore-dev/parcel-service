from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field
from tiacore_lib.enums import ServiceType


class ServiceCreateSchema(BaseModel):
    service_type: ServiceType
    contract_id: UUID
    parcel_id: UUID

    class Config:
        from_attributes = True


class ServiceEditSchema(BaseModel):
    service_type: Optional[ServiceType] = Field(None)
    contract_id: Optional[UUID] = Field(None)
    parcel_id: Optional[UUID] = Field(None)

    class Config:
        from_attributes = True


class ServiceResponseSchema(BaseModel):
    service_id: UUID

    class Config:
        from_attributes = True


class ServiceSchema(BaseModel):
    id: UUID = Field(..., alias="service_id")
    service_type: ServiceType
    contract_id: UUID
    price_id: Optional[UUID] = Field(None)
    parcel_id: UUID
    base_value: float
    summ: Optional[float] = Field(None)

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class ServiceListResponseSchema(BaseModel):
    total: int
    services: List[ServiceSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def service_filter_params(
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    service_type: Optional[ServiceType] = Query(None, description="Фильтр по ID сотрудника"),
    contract_id: Optional[UUID] = Query(None, description="Фильтр по ID сотрудника"),
    price_id: Optional[UUID] = Query(None, description="Фильтр по ID сотрудника"),
    sort_by: Literal["service_type", "created_at"] = Query("created_at", description="Поле для сортировки"),
    order: Literal["asc", "desc"] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "service_type": service_type,
        "parcel_id": parcel_id,
        "contract_id": contract_id,
        "price_id": price_id,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
