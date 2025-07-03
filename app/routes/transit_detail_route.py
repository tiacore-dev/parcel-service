from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import (
    Parcel,
    ParcelStatus,
    ParcelStatusEnum,
    Transit,
    TransitDetails,
)
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.transit_details_models import (
    TransitDetailsCreateSchema,
    TransitDetailsEditSchema,
    TransitDetailsListResponseSchema,
    TransitDetailsResponseSchema,
    TransitDetailsSchema,
    transit_details_filter_params,
)

transit_details_router = APIRouter()


@transit_details_router.post(
    "/add",
    response_model=TransitDetailsResponseSchema,
    summary="Добавить деталь транзита",
    status_code=status.HTTP_201_CREATED,
)
async def add_transit_details(
    data: TransitDetailsCreateSchema,
    _: dict = Depends(require_permission_in_context("add_transit_details")),
):
    transit = await Transit.get_or_none(id=data.transit_id)
    if not transit:
        raise HTTPException(status_code=400, detail="Транзита не существует")
    await validate_exists(Parcel, data.parcel_id, "Накладная")

    detail = await TransitDetails.create(**data.model_dump())
    await ParcelStatus.create(
        parcel_id=data.parcel_id,
        document_id=detail.id,
        status=ParcelStatusEnum.IN_TRANSIT,
        date=transit.date,
    )
    await recalculate_parcel_status(data.parcel_id)
    return TransitDetailsResponseSchema(details_id=detail.id)


@transit_details_router.get(
    "/all",
    response_model=TransitDetailsListResponseSchema,
    summary="Получение списка деталей транзита",
)
async def get_transit_details_list(
    filters: dict = Depends(transit_details_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_transit_details")),
):
    query = Q()

    if filters.get("transit_id"):
        query &= Q(transit_id=filters["transit_id"])

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    sort_by = filters.get("sort_by", "id")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await TransitDetails.filter(query).count()
    details = (
        await TransitDetails.filter(query)
        .order_by(sort_field)
        .offset(offset)
        .limit(page_size)
    )

    return TransitDetailsListResponseSchema(
        total=total_count,
        details=[
            TransitDetailsSchema.model_validate(obj, from_attributes=True)
            for obj in details
        ],
    )


@transit_details_router.get(
    "/{details_id}",
    response_model=TransitDetailsSchema,
    summary="Просмотр одной детали транзита",
)
async def get_transit_details(
    details_id: UUID,
    _: dict = Depends(require_permission_in_context("view_transit_details")),
):
    detail = await TransitDetails.filter(id=details_id).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")

    return TransitDetailsSchema.model_validate(detail, from_attributes=True)


@transit_details_router.patch(
    "/{details_id}",
    response_model=TransitDetailsResponseSchema,
    summary="Редактирование детали транзита",
)
async def edit_transit_details(
    details_id: UUID,
    data: TransitDetailsEditSchema,
    _: dict = Depends(require_permission_in_context("edit_transit_details")),
):
    detail = (
        await TransitDetails.filter(id=details_id).prefetch_related("parcel").first()
    )

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")

    await detail.update_from_dict(data.model_dump(exclude_unset=True))
    await detail.save()
    await recalculate_parcel_status(detail.parcel.id)
    return TransitDetailsResponseSchema(details_id=detail.id)


@transit_details_router.delete(
    "/{details_id}",
    summary="Удаление детали транзита",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_transit_details(
    details_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_transit_details")),
):
    detail = (
        await TransitDetails.filter(id=details_id).prefetch_related("parcel").first()
    )

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")
    await recalculate_parcel_status(detail.parcel.id)
    await detail.delete()
    return
