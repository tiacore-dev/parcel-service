from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Parcel, ParcelStatus, ParcelStatusEnum, PickupFromSender
from app.pydantic_models.pickup_models import (
    PickupFromSenderCreateSchema,
    PickupFromSenderEditSchema,
    PickupFromSenderListResponseSchema,
    PickupFromSenderResponseSchema,
    PickupFromSenderSchema,
    pickup_from_sender_filter_params,
)

pickup_router = APIRouter()


@pickup_router.post(
    "/add",
    response_model=PickupFromSenderResponseSchema,
    summary="Добавить событие получения от отправителя",
    status_code=status.HTTP_201_CREATED,
)
async def add_pickup_from_sender(
    data: PickupFromSenderCreateSchema,
    _: dict = Depends(require_permission_in_context("add_pickup_from_sender")),
):
    await validate_exists(Parcel, data.parcel_id, "Накладная")
    pickup = await PickupFromSender.create(**data.model_dump())
    await ParcelStatus.create(
        parcel_id=data.parcel_id,
        document_id=pickup.id,
        status=ParcelStatusEnum.WITH_EMPLOYEE,
        date=data.date,
        value=data.employee_id,
    )
    return PickupFromSenderResponseSchema(pickup_id=pickup.id)


@pickup_router.get(
    "/all",
    response_model=PickupFromSenderListResponseSchema,
    summary="Получение списка событий получения от отправителя",
)
async def get_pickup_from_sender_list(
    filters: dict = Depends(pickup_from_sender_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_pickup_from_sender")),
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

    total_count = await PickupFromSender.filter(query).count()
    pickups = (
        await PickupFromSender.filter(query)
        .order_by(sort_field)
        .offset(offset)
        .limit(page_size)
    )

    return PickupFromSenderListResponseSchema(
        total=total_count,
        pickups=[
            PickupFromSenderSchema.model_validate(obj, from_attributes=True)
            for obj in pickups
        ],
    )


@pickup_router.get(
    "/{pickup_id}",
    response_model=PickupFromSenderSchema,
    summary="Просмотр одного события получения от отправителя",
)
async def get_pickup_from_sender(
    pickup_id: UUID,
    _: dict = Depends(require_permission_in_context("view_pickup_from_sender")),
):
    pickup = await PickupFromSender.filter(id=pickup_id).first()

    if not pickup:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    return PickupFromSenderSchema.model_validate(pickup, from_attributes=True)


@pickup_router.patch(
    "/{pickup_id}",
    response_model=PickupFromSenderResponseSchema,
    summary="Редактирование события получения от отправителя",
)
async def edit_pickup_from_sender(
    pickup_id: UUID,
    data: PickupFromSenderEditSchema,
    _: dict = Depends(require_permission_in_context("edit_pickup_from_sender")),
):
    pickup = await PickupFromSender.filter(id=pickup_id).first()

    if not pickup:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    await pickup.update_from_dict(data.model_dump(exclude_unset=True))
    await pickup.save()

    return PickupFromSenderResponseSchema(pickup_id=pickup.id)


@pickup_router.delete(
    "/{pickup_id}",
    summary="Удаление события получения от отправителя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_pickup_from_sender(
    pickup_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_pickup_from_sender")),
):
    pickup = await PickupFromSender.filter(id=pickup_id).first()

    if not pickup:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    await pickup.delete()
    return
