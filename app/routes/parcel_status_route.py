from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import ParcelStatus
from app.pydantic_models.parcel_status_models import (
    ParcelStatusListResponseSchema,
    ParcelStatusSchema,
    parcel_status_filter_params,
)

parcel_status_router = APIRouter()


@parcel_status_router.get(
    "/all",
    response_model=ParcelStatusListResponseSchema,
    summary="Получение списка статусов накладных",
)
async def get_parcel_statuses(
    filters: dict = Depends(parcel_status_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_parcel_statuses")),
):
    query = Q()

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    if filters.get("document_id"):
        query &= Q(document_id=filters["document_id"])

    if filters.get("status"):
        query &= Q(status=filters["status"])

    if filters.get("value"):
        query &= Q(value=filters["value"])

    if filters.get("document_type"):
        query &= Q(document_type=filters["document_type"])

    if filters.get("value_type"):
        query &= Q(value_type=filters["value_type"])

    sort_by = filters.get("sort_by", "status")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await ParcelStatus.filter(query).count()
    statuses = await ParcelStatus.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return ParcelStatusListResponseSchema(
        total=total_count,
        statuses=[ParcelStatusSchema.model_validate(obj, from_attributes=True) for obj in statuses],
    )


@parcel_status_router.get(
    "/{status_id}",
    response_model=ParcelStatusSchema,
    summary="Просмотр одного статуса накладной",
)
async def get_parcel_status_by_id(
    status_id: UUID,
    _: dict = Depends(require_permission_in_context("view_parcel_status")),
):
    status_obj = await ParcelStatus.filter(id=status_id).first()

    if not status_obj:
        raise HTTPException(status_code=404, detail="Статус не найден")

    return ParcelStatusSchema.model_validate(status_obj, from_attributes=True)
