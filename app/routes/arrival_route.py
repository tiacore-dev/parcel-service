from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Arrival, ArrivalDetails
from app.pydantic_models.arrival_models import (
    ArrivalCreateBulkSchema,
    ArrivalCreateSchema,
    ArrivalEditSchema,
    ArrivalListResponseSchema,
    ArrivalResponseSchema,
    ArrivalSchema,
    arrival_filter_params,
)

arrival_router = APIRouter()


@arrival_router.post(
    "/add",
    response_model=ArrivalResponseSchema,
    summary="Добавить событие поступления на склад",
    status_code=status.HTTP_201_CREATED,
)
async def add_arrival(
    data: ArrivalCreateSchema,
    context: dict = Depends(require_permission_in_context("add_arrival")),
):
    arrival = await Arrival.create(created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump())

    return ArrivalResponseSchema(arrival_id=arrival.id)


@arrival_router.post(
    "/add-bulk",
    response_model=ArrivalResponseSchema,
    summary="Добавить транзит",
    status_code=status.HTTP_201_CREATED,
)
async def add_bulk_arrival(
    data: ArrivalCreateBulkSchema,
    context: dict = Depends(require_permission_in_context("add_arrival_bulk")),
):
    create_data = data.model_dump()

    create_data.pop("parcels")
    arrival = await Arrival.create(created_by=context["user_id"], modified_by=context["user_id"], **create_data)
    await ArrivalDetails.bulk_create(
        [
            ArrivalDetails(
                created_by=context["user_id"], modified_by=context["user_id"], parcel_id=parcel, arrival=arrival
            )
            for parcel in data.parcels
        ]
    )
    return ArrivalResponseSchema(arrival_id=arrival.id)


@arrival_router.get(
    "/all",
    response_model=ArrivalListResponseSchema,
    summary="Получение списка событий поступления на склад",
)
async def get_arrival_list(
    filters: dict = Depends(arrival_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_arrivals")),
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

    total_count = await Arrival.filter(query).count()
    arrivals = (
        await Arrival.filter(query)
        .prefetch_related("arrival_details__parcel")
        .order_by(sort_field)
        .offset(offset)
        .limit(page_size)
    )
    arrival_schemas = []
    for arrival in arrivals:
        parcels = []

        for detail in await arrival.arrival_details.all():
            parcel = await detail.parcel
            if parcel:
                parcels.append(
                    {
                        "parcel_name": parcel.name,
                        "places_count": parcel.places_count,
                        "recipient_city": parcel.recipient_city,
                        "volume": parcel.volume,
                        "weight": parcel.weight,
                        "recipient_additional_info": parcel.recipient_additional_info,
                    }
                )

        arrival_dict = arrival.__dict__.copy()

        arrival_dict["parcel_count"] = len(parcels)
        arrival_dict["parcels"] = parcels

        arrival_schemas.append(ArrivalSchema.model_validate(arrival_dict, from_attributes=True))

    return ArrivalListResponseSchema(
        total=total_count,
        arrivals=arrival_schemas,
    )


@arrival_router.get(
    "/{arrival_id}",
    response_model=ArrivalSchema,
    summary="Просмотр одного события поступления на склад",
)
async def get_arrival(
    arrival_id: UUID,
    _: dict = Depends(require_permission_in_context("view_arrival")),
):
    arrival = await Arrival.filter(id=arrival_id).first()

    if not arrival:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    return ArrivalSchema.model_validate(arrival, from_attributes=True)


@arrival_router.patch(
    "/{arrival_id}",
    response_model=ArrivalResponseSchema,
    summary="Редактирование события поступления на склад",
)
async def edit_arrival(
    arrival_id: UUID,
    data: ArrivalEditSchema,
    context: dict = Depends(require_permission_in_context("edit_arrival")),
):
    arrival = await Arrival.filter(id=arrival_id).first()

    if not arrival:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    await arrival.update_from_dict(data.model_dump(exclude_unset=True))
    arrival.modified_by = context["user_id"]
    await arrival.save()

    return ArrivalResponseSchema(arrival_id=arrival.id)


@arrival_router.delete(
    "/{arrival_id}",
    summary="Удаление события поступления на склад",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_arrival(
    arrival_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_arrival")),
):
    arrival = await Arrival.filter(id=arrival_id).first()

    if not arrival:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    await arrival.delete()
    return
