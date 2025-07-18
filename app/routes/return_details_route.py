from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Parcel, ParcelStatus, ParcelStatusEnum, Return, ReturnDetails
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.return_details_models import (
    ReturnDetailsCreateSchema,
    ReturnDetailsEditSchema,
    ReturnDetailsListResponseSchema,
    ReturnDetailsResponseSchema,
    ReturnDetailsSchema,
    return_details_filter_params,
)

return_details_router = APIRouter()


@return_details_router.post(
    "/add",
    response_model=ReturnDetailsResponseSchema,
    summary="Добавить деталь транзита",
    status_code=status.HTTP_201_CREATED,
)
async def add_return_details(
    data: ReturnDetailsCreateSchema,
    context: dict = Depends(require_permission_in_context("add_return_details")),
):
    return_obj = await Return.get_or_none(id=data.returns_id)
    if not return_obj:
        raise HTTPException(status_code=400, detail="Транзита не существует")
    await validate_exists(Parcel, data.parcel_id, "Накладная")

    detail = await ReturnDetails.create(
        created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump()
    )
    await ParcelStatus.create(
        parcel_id=data.parcel_id,
        document_id=return_obj.id,
        document_type="return_id",
        status=ParcelStatusEnum.RETURNED,
        date=return_obj.date,
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(data.parcel_id)
    return ReturnDetailsResponseSchema(details_id=detail.id)


@return_details_router.get(
    "/all",
    response_model=ReturnDetailsListResponseSchema,
    summary="Получение списка деталей транзита",
)
async def get_return_details_list(
    filters: dict = Depends(return_details_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_return_details")),
):
    query = Q()

    if filters.get("return_id"):
        query &= Q(return_id=filters["return_id"])

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

    total_count = await ReturnDetails.filter(query).count()
    details = (
        await ReturnDetails.filter(query)
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

        detail_schemas.append(ReturnDetailsSchema.model_validate(combined_data))

    return ReturnDetailsListResponseSchema(
        total=total_count,
        details=detail_schemas,
    )


@return_details_router.get(
    "/{details_id}",
    response_model=ReturnDetailsSchema,
    summary="Просмотр одной детали транзита",
)
async def get_return_details(
    details_id: UUID,
    _: dict = Depends(require_permission_in_context("view_return_details")),
):
    detail = await ReturnDetails.filter(id=details_id).first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")

    return ReturnDetailsSchema.model_validate(detail, from_attributes=True)


@return_details_router.patch(
    "/{details_id}",
    response_model=ReturnDetailsResponseSchema,
    summary="Редактирование детали транзита",
)
async def edit_return_details(
    details_id: UUID,
    data: ReturnDetailsEditSchema,
    context: dict = Depends(require_permission_in_context("edit_return_details")),
):
    detail = await ReturnDetails.filter(id=details_id).prefetch_related("parcel", "returns").first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")

    await detail.update_from_dict(data.model_dump(exclude_unset=True))
    detail.modified_by = context["user_id"]
    await detail.save()
    await ParcelStatus.filter(document_id=detail.returns.id).delete()
    await ParcelStatus.create(
        parcel_id=detail.parcel.id,
        document_id=detail.returns.id,
        document_type="return_id",
        status=ParcelStatusEnum.RETURNED,
        date=detail.returns.date,
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(detail.parcel.id)
    return ReturnDetailsResponseSchema(details_id=detail.id)


@return_details_router.delete(
    "/{details_id}",
    summary="Удаление детали транзита",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_return_details(
    details_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_return_details")),
):
    detail = await ReturnDetails.filter(id=details_id).prefetch_related("parcel").first()

    if not detail:
        raise HTTPException(status_code=404, detail="Деталь транзита не найдена")
    parcel_id = detail.parcel.id
    await detail.delete()
    await recalculate_parcel_status(parcel_id)
    return
