from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field

from app.database.models import ParcelStatusEnum  # если Enum у тебя лежит тут

# class ParcelStatusCreateSchema(BaseModel):
#     parcel_id: UUID
#     document_id: UUID
#     status: ParcelStatusEnum
#     value: UUID
#     comment: Optional[str] = None

#     class Config:
#         from_attributes = True


# class ParcelStatusEditSchema(BaseModel):
#     document_id: Optional[UUID] = None
#     status: Optional[ParcelStatusEnum] = None
#     value: Optional[UUID] = None
#     comment: Optional[str] = None

#     class Config:
#         from_attributes = True


# class ParcelStatusResponseSchema(BaseModel):
#     status_id: UUID

#     class Config:
#         from_attributes = True


class ParcelStatusSchema(BaseModel):
    id: UUID = Field(..., alias="status_id")
    parcel_id: UUID
    document_id: UUID
    status: ParcelStatusEnum
    value: UUID
    comment: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class ParcelStatusListResponseSchema(BaseModel):
    total: int
    statuses: List[ParcelStatusSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def parcel_status_filter_params(
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    document_id: Optional[UUID] = Query(None, description="Фильтр по ID документа"),
    status: Optional[ParcelStatusEnum] = Query(None, description="Статус"),
    value: Optional[UUID] = Query(None, description="Значение"),
    sort_by: Optional[str] = Query("status", description="Поле для сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_id": parcel_id,
        "document_id": document_id,
        "status": status,
        "value": value,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
