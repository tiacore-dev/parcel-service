from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import (
    ArrivalToWarehouse,
    Parcel,
    ParcelStatus,
    ParcelStatusEnum,
)
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.arrival_warehouse_models import (
    ArrivalToWarehouseCreateSchema,
    ArrivalToWarehouseEditSchema,
    ArrivalToWarehouseListResponseSchema,
    ArrivalToWarehouseResponseSchema,
    ArrivalToWarehouseSchema,
    arrival_to_warehouse_filter_params,
)

arrival_to_warehouse_router = APIRouter()


@arrival_to_warehouse_router.post(
    "/add",
    response_model=ArrivalToWarehouseResponseSchema,
    summary="Добавить событие поступления на склад",
    status_code=status.HTTP_201_CREATED,
)
async def add_arrival_to_warehouse(
    data: ArrivalToWarehouseCreateSchema,
    _: dict = Depends(require_permission_in_context("add_arrival_to_warehouse")),
):
    await validate_exists(Parcel, data.parcel_id, "Накладная")
    arrival = await ArrivalToWarehouse.create(**data.model_dump())
    await ParcelStatus.create(
        parcel_id=data.parcel_id,
        document_id=arrival.id,
        status=ParcelStatusEnum.ON_WAREHOUSE,
        date=data.date,
        value=data.warehouse_id,
    )
    await recalculate_parcel_status(data.parcel_id)
    return ArrivalToWarehouseResponseSchema(arrival_id=arrival.id)


@arrival_to_warehouse_router.get(
    "/all",
    response_model=ArrivalToWarehouseListResponseSchema,
    summary="Получение списка событий поступления на склад",
)
async def get_arrival_to_warehouse_list(
    filters: dict = Depends(arrival_to_warehouse_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_arrivals_to_warehouse")),
):
    query = Q()

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    if filters.get("warehouse_id"):
        query &= Q(warehouse_id=filters["warehouse_id"])

    if filters.get("date_from"):
        query &= Q(date__gte=filters["date_from"])

    if filters.get("date_to"):
        query &= Q(date__lte=filters["date_to"])

    sort_by = filters.get("sort_by", "date")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await ArrivalToWarehouse.filter(query).count()
    arrivals = (
        await ArrivalToWarehouse.filter(query)
        .order_by(sort_field)
        .offset(offset)
        .limit(page_size)
    )

    return ArrivalToWarehouseListResponseSchema(
        total=total_count,
        arrivals=[
            ArrivalToWarehouseSchema.model_validate(obj, from_attributes=True)
            for obj in arrivals
        ],
    )


@arrival_to_warehouse_router.get(
    "/{arrival_id}",
    response_model=ArrivalToWarehouseSchema,
    summary="Просмотр одного события поступления на склад",
)
async def get_arrival_to_warehouse(
    arrival_id: UUID,
    _: dict = Depends(require_permission_in_context("view_arrival_to_warehouse")),
):
    arrival = await ArrivalToWarehouse.filter(id=arrival_id).first()

    if not arrival:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    return ArrivalToWarehouseSchema.model_validate(arrival, from_attributes=True)


@arrival_to_warehouse_router.patch(
    "/{arrival_id}",
    response_model=ArrivalToWarehouseResponseSchema,
    summary="Редактирование события поступления на склад",
)
async def edit_arrival_to_warehouse(
    arrival_id: UUID,
    data: ArrivalToWarehouseEditSchema,
    _: dict = Depends(require_permission_in_context("edit_arrival_to_warehouse")),
):
    arrival = (
        await ArrivalToWarehouse.filter(id=arrival_id)
        .prefetch_related("parcel")
        .first()
    )

    if not arrival:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    await recalculate_parcel_status(arrival.parcel.id)
    await arrival.update_from_dict(data.model_dump(exclude_unset=True))
    await arrival.save()

    return ArrivalToWarehouseResponseSchema(arrival_id=arrival.id)


@arrival_to_warehouse_router.delete(
    "/{arrival_id}",
    summary="Удаление события поступления на склад",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_arrival_to_warehouse(
    arrival_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_arrival_to_warehouse")),
):
    arrival = (
        await ArrivalToWarehouse.filter(id=arrival_id)
        .prefetch_related("parcel")
        .first()
    )

    if not arrival:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    await recalculate_parcel_status(arrival.parcel.id)
    await arrival.delete()
    return
