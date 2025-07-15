from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel, Field


class CargoTypeCreateSchema(BaseModel):
    name: str = Field(..., alias="cargo_type_name")
    company_id: UUID

    class Config:
        from_attributes = True


class CargoTypeEditSchema(BaseModel):
    name: Optional[str] = Field(None, alias="cargo_type_name")
    company_id: Optional[UUID] = Field(None)

    class Config:
        from_attributes = True


class CargoTypeResponseSchema(BaseModel):
    cargo_type_id: UUID

    class Config:
        from_attributes = True


class CargoTypeSchema(BaseModel):
    id: UUID = Field(..., alias="cargo_type_id")
    name: str = Field(..., alias="cargo_type_name")
    company_id: UUID

    created_at: datetime = Field(...)
    created_by: UUID = Field(...)
    modified_at: datetime = Field(...)
    modified_by: UUID = Field(...)

    class Config:
        from_attributes = True
        populate_by_name = True


class CargoTypeListResponseSchema(BaseModel):
    total: int
    types: List[CargoTypeSchema]

    class Config:
        from_attributes = True
        populate_by_name = True


def cargo_type_filter_params(
    company_id: Optional[UUID] = Query(None, description="Артикул"),
    cargo_type_name: Optional[bool] = Query(None, description="Статус доставки"),
    sort_by: Optional[str] = Query("name", description="Поле сортировки"),
    order: Optional[str] = Query("asc", description="asc/desc"),
    page: Optional[int] = Query(1, ge=1, description="Номер страницы"),
    page_size: Optional[int] = Query(10, ge=1, le=100, description="Размер страницы"),
):
    return {
        "company_id": company_id,
        "cargo_type_name": cargo_type_name,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
