from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field

from app.pydantic_models.parcel_models import ParcelShortSchema


class IssueCreateSchema(BaseModel):
    employee_id: UUID
    date: datetime

    class Config:
        from_attributes = True


class IssueCreateBulkSchema(BaseModel):
    employee_id: UUID
    date: datetime
    parcels: List[UUID]

    class Config:
        from_attributes = True


class IssueEditSchema(BaseModel):
    employee_id: Optional[UUID] = None
    date: Optional[datetime] = None

    class Config:
        from_attributes = True


class IssueResponseSchema(BaseModel):
    issue_id: UUID

    class Config:
        from_attributes = True


class IssueSchema(BaseModel):
    id: UUID = Field(..., alias="issue_id")
    employee_id: UUID
    date: datetime
    parcel_count: Optional[int] = Field(None)
    parcels: Optional[List[ParcelShortSchema]] = Field(None)

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class IssueListResponseSchema(BaseModel):
    total: int
    issues: List[IssueSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def issue_filter_params(
    parcel_name: Optional[str] = Query(None, description="Фильтр по номеру накладной"),
    parcel_id: Optional[UUID] = Query(None, description="Фильтр по ID накладной"),
    employee_id: Optional[UUID] = Query(None, description="Фильтр по ID сотрудника"),
    date_from: Optional[datetime] = Query(None, description="Дата от (включительно)"),
    date_to: Optional[datetime] = Query(None, description="Дата до (включительно)"),
    sort_by: Literal["date", "created_at"] = Query("date", description="Поле для сортировки"),
    order: Literal["asc", "desc"] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "parcel_name": parcel_name,
        "parcel_id": parcel_id,
        "employee_id": employee_id,
        "date_from": date_from,
        "date_to": date_to,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
