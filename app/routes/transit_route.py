from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Transit, TransitDetails
from app.pydantic_models.transit_models import (
    TransitCreateBulkSchema,
    TransitCreateSchema,
    TransitEditSchema,
    TransitListResponseSchema,
    TransitResponseSchema,
    TransitSchema,
    transit_filter_params,
)
from app.utils.db_helpers import generate_transit_number

transit_router = APIRouter()


@transit_router.post(
    "/add",
    response_model=TransitResponseSchema,
    summary="Добавить транзит",
    status_code=status.HTTP_201_CREATED,
)
async def add_transit(
    data: TransitCreateSchema,
    context: dict = Depends(require_permission_in_context("add_transit")),
):
    create_data = data.model_dump()
    if not data.name:
        create_data["name"] = await generate_transit_number()
    transit = await Transit.create(created_by=context["user_id"], modified_by=context["user_id"], **create_data)

    return TransitResponseSchema(transit_id=transit.id)


@transit_router.post(
    "/add-bulk",
    response_model=TransitResponseSchema,
    summary="Добавить транзит",
    status_code=status.HTTP_201_CREATED,
)
async def add_bulk_transit(
    data: TransitCreateBulkSchema,
    context: dict = Depends(require_permission_in_context("add_transit_bulk")),
):
    create_data = data.model_dump()
    if not data.name:
        create_data["name"] = await generate_transit_number()
    create_data.pop("parcels")
    transit = await Transit.create(created_by=context["user_id"], modified_by=context["user_id"], **create_data)
    await TransitDetails.bulk_create(
        [
            TransitDetails(
                created_by=context["user_id"], modified_by=context["user_id"], parcel_id=parcel, transit=transit
            )
            for parcel in data.parcels
        ]
    )
    return TransitResponseSchema(transit_id=transit.id)


@transit_router.get(
    "/all",
    response_model=TransitListResponseSchema,
    summary="Получение списка транзитов",
)
async def get_transit_list(
    filters: dict = Depends(transit_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_transits")),
):
    query = Q()

    if filters.get("warehouse_from_id"):
        query &= Q(warehouse_from_id=filters["warehouse_from_id"])

    if filters.get("warehouse_to_id"):
        query &= Q(warehouse_to_id=filters["warehouse_to_id"])

    if filters.get("date_from"):
        query &= Q(date__gte=filters["date_from"])

    if filters.get("date_to"):
        query &= Q(date__lte=filters["date_to"])

    if filters.get("status"):
        query &= Q(status=filters["status"])

    if filters.get("transit_name"):
        query &= Q(name__icontains=filters["transit_name"])

    sort_by = filters.get("sort_by", "date")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await Transit.filter(query).count()
    transits = (
        await Transit.filter(query)
        .prefetch_related("transit_details__parcel")
        .order_by(sort_field)
        .offset(offset)
        .limit(page_size)
    )

    transit_schemas = []
    for transit in transits:
        parcels = []
        for detail in await transit.transit_details.all():
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

        transit_dict = transit.__dict__.copy()
        transit_dict["parcel_count"] = len(parcels)
        transit_dict["parcels"] = parcels

        transit_schemas.append(TransitSchema.model_validate(transit_dict, from_attributes=True))

    return TransitListResponseSchema(
        total=total_count,
        transits=transit_schemas,
    )


@transit_router.get(
    "/{transit_id}",
    response_model=TransitSchema,
    summary="Просмотр одного транзита",
)
async def get_transit(
    transit_id: UUID,
    _: dict = Depends(require_permission_in_context("view_transit")),
):
    transit = await Transit.filter(id=transit_id).first()

    if not transit:
        raise HTTPException(status_code=404, detail="Транзит не найден")

    return TransitSchema.model_validate(transit, from_attributes=True)


@transit_router.patch(
    "/{transit_id}",
    response_model=TransitResponseSchema,
    summary="Редактирование транзита",
)
async def edit_transit(
    transit_id: UUID,
    data: TransitEditSchema,
    context: dict = Depends(require_permission_in_context("edit_transit")),
):
    transit = await Transit.filter(id=transit_id).first()

    if not transit:
        raise HTTPException(status_code=404, detail="Транзит не найден")

    await transit.update_from_dict(data.model_dump(exclude_unset=True))
    transit.modified_by = context["user_id"]
    await transit.save()

    return TransitResponseSchema(transit_id=transit.id)


@transit_router.delete(
    "/{transit_id}",
    summary="Удаление транзита",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_transit(
    transit_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_transit")),
):
    transit = await Transit.filter(id=transit_id).first()

    if not transit:
        raise HTTPException(status_code=404, detail="Транзит не найден")

    await transit.delete()
    return
