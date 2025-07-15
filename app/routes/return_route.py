from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Parcel, ParcelStatus, ParcelStatusEnum, ReturnToSender
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.return_models import (
    ReturnToSenderCreateSchema,
    ReturnToSenderEditSchema,
    ReturnToSenderListResponseSchema,
    ReturnToSenderResponseSchema,
    ReturnToSenderSchema,
    return_to_sender_filter_params,
)

return_router = APIRouter()


@return_router.post(
    "/add",
    response_model=ReturnToSenderResponseSchema,
    summary="Добавить событие возврата отправителю",
    status_code=status.HTTP_201_CREATED,
)
async def add_return_to_sender(
    data: ReturnToSenderCreateSchema,
    context: dict = Depends(require_permission_in_context("add_return_to_sender")),
):
    await validate_exists(Parcel, data.parcel_id, "Накладная")
    return_obj = await ReturnToSender.create(
        created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump()
    )
    await ParcelStatus.create(
        parcel_id=data.parcel_id,
        document_id=return_obj.id,
        document_type="return_id",
        status=ParcelStatusEnum.RETURNED,
        date=data.date,
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(data.parcel_id)
    return ReturnToSenderResponseSchema(return_id=return_obj.id)


@return_router.get(
    "/all",
    response_model=ReturnToSenderListResponseSchema,
    summary="Получение списка возвратов отправителю",
)
async def get_return_to_sender_list(
    filters: dict = Depends(return_to_sender_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_returns_to_sender")),
):
    query = Q()

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    if filters.get("warehouse_id"):
        query &= Q(warehouse_id=filters["warehouse_id"])

    if filters.get("employee_id"):
        query &= Q(employee_id=filters["employee_id"])

    if filters.get("date_from"):
        query &= Q(date__gte=filters["date_from"])

    if filters.get("date_to"):
        query &= Q(date__lte=filters["date_to"])

    if filters.get("sender_name"):
        query &= Q(sender_name__icontains=filters["sender_name"])

    sort_by = filters.get("sort_by", "date")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await ReturnToSender.filter(query).count()
    returns = await ReturnToSender.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return ReturnToSenderListResponseSchema(
        total=total_count,
        returns=[ReturnToSenderSchema.model_validate(obj, from_attributes=True) for obj in returns],
    )


@return_router.get(
    "/{return_id}",
    response_model=ReturnToSenderSchema,
    summary="Просмотр одного события возврата отправителю",
)
async def get_return_to_sender(
    return_id: UUID,
    _: dict = Depends(require_permission_in_context("view_return_to_sender")),
):
    return_obj = await ReturnToSender.filter(id=return_id).first()

    if not return_obj:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    return ReturnToSenderSchema.model_validate(return_obj, from_attributes=True)


@return_router.patch(
    "/{return_id}",
    response_model=ReturnToSenderResponseSchema,
    summary="Редактирование события возврата отправителю",
)
async def edit_return_to_sender(
    return_id: UUID,
    data: ReturnToSenderEditSchema,
    context: dict = Depends(require_permission_in_context("edit_return_to_sender")),
):
    return_obj = await ReturnToSender.filter(id=return_id).prefetch_related("parcel").first()

    if not return_obj:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    await return_obj.update_from_dict(data.model_dump(exclude_unset=True))
    return_obj.modified_by = context["user_id"]
    await return_obj.save()
    await ParcelStatus.filter(document_id=return_id).delete()
    await ParcelStatus.create(
        parcel_id=return_obj.parcel.id,
        document_id=return_obj.id,
        document_type="return_id",
        status=ParcelStatusEnum.RETURNED,
        date=return_obj.date,
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(return_obj.parcel.id)

    return ReturnToSenderResponseSchema(return_id=return_obj.id)


@return_router.delete(
    "/{return_id}",
    summary="Удаление события возврата отправителю",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_return_to_sender(
    return_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_return_to_sender")),
):
    return_obj = await ReturnToSender.filter(id=return_id).prefetch_related("parcel").first()

    if not return_obj:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    await ParcelStatus.filter(document_id=return_id).delete()
    await recalculate_parcel_status(return_obj.parcel.id)
    await return_obj.delete()
    return
