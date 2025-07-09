from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Parcel
from app.handlers.status_handler import get_cached_parcel_status_data
from app.pydantic_models.parcel_models import (
    ParcelCreateSchema,
    ParcelCurrentStatusSchema,
    ParcelEditSchema,
    ParcelListResponseSchema,
    ParcelResponseSchema,
    ParcelSchema,
    parcel_filter_params,
)

parcel_router = APIRouter()


@parcel_router.post(
    "/add",
    response_model=ParcelResponseSchema,
    summary="Добавить накладную",
    status_code=status.HTTP_201_CREATED,
)
async def add_parcel(
    data: ParcelCreateSchema,
    _t=Depends(require_permission_in_context("add_parcel")),
):
    parcel = await Parcel.create(**data.model_dump())

    return ParcelResponseSchema(parcel_id=parcel.id)


@parcel_router.patch(
    "/{parcel_id}",
    response_model=ParcelResponseSchema,
    summary="Изменение накладной",
)
async def edit_parcel(
    parcel_id: UUID,
    data: ParcelEditSchema,
    _: dict = Depends(require_permission_in_context("delete_parcel")),
):
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="")

    await parcel.update_from_dict(data.model_dump(exclude_unset=True))
    await parcel.save()

    return ParcelResponseSchema(parcel_id=parcel.id)


@parcel_router.delete(
    "/{parcel_id}",
    summary="Удаление накладной",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_parcel(
    parcel_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_parcel")),
):
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="")

    await parcel.delete()


@parcel_router.get(
    "/all",
    response_model=ParcelListResponseSchema,
    summary="Получение списка накладных",
)
async def get_parcels(
    filters: dict = Depends(parcel_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_parcels")),
):
    query = Q()
    if filters.get("parcel_name"):
        query &= Q(name__icontains=filters["parcel_name"])

    if filters.get("sender_city"):
        query &= Q(sender_city=filters["sender_city"])

    if filters.get("recipient_city"):
        query &= Q(recipient_city=filters["recipient_city"])

    if filters.get("sender_warehouse"):
        query &= Q(sender_warehouse=filters["sender_warehouse"])

    if filters.get("recipient_warehouse"):
        query &= Q(recipient_warehouse=filters["recipient_warehouse"])

    if filters.get("pickup_date_from"):
        query &= Q(pickup_estimated_date__gte=filters["pickup_date_from"])

    if filters.get("pickup_date_to"):
        query &= Q(pickup_estimated_date__lte=filters["pickup_date_to"])

    if filters.get("delivery_date_from"):
        query &= Q(delivery_estimated_date__gte=filters["delivery_date_from"])

    if filters.get("delivery_date_to"):
        query &= Q(delivery_estimated_date__lte=filters["delivery_date_to"])

    if filters.get("min_weight"):
        query &= Q(weight__gte=filters["min_weight"])

    if filters.get("max_weight"):
        query &= Q(weight__lte=filters["max_weight"])

    if filters.get("min_volume"):
        query &= Q(volume__gte=filters["min_volume"])

    if filters.get("max_volume"):
        query &= Q(volume__lte=filters["max_volume"])

    if filters.get("sender_company"):
        query &= Q(sender_company__icontains=filters["sender_company"])

    if filters.get("recipient_company"):
        query &= Q(recipient_company__icontains=filters["recipient_company"])

    if filters.get("company_id"):
        query &= Q(company_id=filters["company_id"])

    if filters.get("search"):
        query &= (
            Q(sender_address__icontains=filters["search"])
            | Q(recipient_address__icontains=filters["search"])
            | Q(sender_company__icontains=filters["search"])
            | Q(recipient_company__icontains=filters["search"])
        )

    sort_by = filters.get("sort_by", "created_at")
    if sort_by == "parcel_name":
        sort_by = "name"
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await Parcel.filter(query).count()
    parcels = await Parcel.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return ParcelListResponseSchema(
        total=total_count,
        parcels=[ParcelSchema.model_validate(parcel, from_attributes=True) for parcel in parcels],
    )


@parcel_router.get(
    "/{parcel_id}/status",
    response_model=Optional[ParcelCurrentStatusSchema],
    summary="Получение актуального статуса накладной",
)
async def get_parcel_status(
    parcel_id: UUID,
    _: dict = Depends(require_permission_in_context("get_parcel_current_status")),
):
    data = await get_cached_parcel_status_data(parcel_id=parcel_id)
    if not data:
        return None
    return ParcelCurrentStatusSchema(**data)


@parcel_router.get(
    "/{parcel_id}",
    response_model=ParcelSchema,
    summary="Просмотр одной накладной",
)
async def get_legal_parcel(
    parcel_id: UUID,
    _: dict = Depends(require_permission_in_context("view_parcel")),
):
    parcel = await Parcel.filter(id=parcel_id).first()

    if not parcel:
        raise HTTPException(status_code=404, detail="Накладная не найдена")

    return ParcelSchema.model_validate(parcel, from_attributes=True)
