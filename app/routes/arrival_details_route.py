from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Arrival, ArrivalDetails, Parcel, ParcelStatus, ParcelStatusEnum
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.arrival_details_models import (
    ArrivalDetailsCreateSchema,
    ArrivalDetailsEditSchema,
    ArrivalDetailsListResponseSchema,
    ArrivalDetailsResponseSchema,
    ArrivalDetailsSchema,
    arrival_details_filter_params,
)

arrival_details_router = APIRouter()


@arrival_details_router.post(
    "/add",
    response_model=ArrivalDetailsResponseSchema,
    summary="Добавить деталь транзита",
    status_code=status.HTTP_201_CREATED,
)
async def add_arrival_details(
    data: ArrivalDetailsCreateSchema,
    context: dict = Depends(require_permission_in_context("add_arrival_details")),
):
    arrival = await Arrival.get_or_none(id=data.arrival_id)
    if not arrival:
        raise HTTPException(status_code=400, detail="Транзита не существует")
    await validate_exists(Parcel, data.parcel_id, "Накладная")

    detail = await ArrivalDetails.create(
        created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump()
    )
    await ParcelStatus.create(
        parcel_id=data.parcel_id,
        document_id=arrival.id,
        document_type="arrival_id",
        status=ParcelStatusEnum.ON_WAREHOUSE,
        date=arrival.date,
        value=arrival.warehouse_id,
        value_type="warehouse_id",
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(data.parcel_id)
    return ArrivalDetailsResponseSchema(details_id=detail.id)


@arrival_details_router.get(
    "/all",
    response_model=ArrivalDetailsListResponseSchema,
    summary="Получение списка деталей транзита",
)
async def get_arrival_details_list(
    filters: dict = Depends(arrival_details_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_arrival_details")),
):
    query = Q()

    if filters.get("arrival_id"):
        query &= Q(arrival_id=filters["arrival_id"])

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    if filters.get("parcel_name"):
        query &= Q(parcel__name__icontains=filters["parcel_name"])

    sort_by = filters.get("sort_by", "id")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await ArrivalDetails.filter(query).count()
    details = (
        await ArrivalDetails.filter(query)
        .order_by(sort_field)
        .offset(offset)
        .limit(page_size)
        .prefetch_related("parcel")
    )
    detail_schemas = []
    for detail in details:
        parcel = await Parcel.get_or_none(id=detail.parcel.id)
        if not parcel:
            raise HTTPException(status_code=400, detail="Накладная не найдена")
        parcel_data = {
            "parcel_name": parcel.name,
            "places_count": parcel.places_count,
            "recipient_city": parcel.recipient_city,
            "volume": parcel.volume,
            "weight": parcel.weight,
            "recipient_additional_info": parcel.recipient_additional_info,
        }
        detail_dict = detail.__dict__

        combined_data = {**detail_dict, **parcel_data}

        detail_schemas.append(ArrivalDetailsSchema.model_validate(combined_data))

    return ArrivalDetailsListResponseSchema(
        total=total_count,
        details=detail_schemas,
    )


@arrival_details_router.get(
    "/{details_id}",
    response_model=ArrivalDetailsSchema,
    summary="Просмотр одной детали транзита",
)
async def get_arrival_details(
    details_id: UUID,
    _: dict = Depends(require_permission_in_context("view_arrival_details")),
):
    detail = await ArrivalDetails.filter(id=details_id).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")

    return ArrivalDetailsSchema.model_validate(detail, from_attributes=True)


@arrival_details_router.patch(
    "/{details_id}",
    response_model=ArrivalDetailsResponseSchema,
    summary="Редактирование детали транзита",
)
async def edit_arrival_details(
    details_id: UUID,
    data: ArrivalDetailsEditSchema,
    context: dict = Depends(require_permission_in_context("edit_arrival_details")),
):
    detail = await ArrivalDetails.filter(id=details_id).prefetch_related("parcel", "arrival").first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")

    await detail.update_from_dict(data.model_dump(exclude_unset=True))
    detail.modified_by = context["user_id"]
    await detail.save()
    await ParcelStatus.filter(document_id=detail.arrival.id).delete()
    await ParcelStatus.create(
        parcel_id=detail.parcel.id,
        document_id=detail.arrival.id,
        document_type="arrival_id",
        status=ParcelStatusEnum.ON_WAREHOUSE,
        date=detail.arrival.date,
        value=detail.arrival.warehouse_id,
        value_type="warehouse_id",
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(detail.parcel.id)
    return ArrivalDetailsResponseSchema(details_id=detail.id)


@arrival_details_router.delete(
    "/{details_id}",
    summary="Удаление детали транзита",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_arrival_details(
    details_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_arrival_details")),
):
    detail = await ArrivalDetails.filter(id=details_id).prefetch_related("parcel").first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")
    parcel_id = detail.parcel.id
    await detail.delete()
    await recalculate_parcel_status(parcel_id)
    return
