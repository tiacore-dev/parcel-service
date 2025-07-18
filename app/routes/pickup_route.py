from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import Parcel, ParcelStatus, ParcelStatusEnum, Pickup
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.pickup_models import (
    PickupCreateSchema,
    PickupEditSchema,
    PickupListResponseSchema,
    PickupResponseSchema,
    PickupSchema,
    pickup_filter_params,
)

pickup_router = APIRouter()


@pickup_router.post(
    "/add",
    response_model=PickupResponseSchema,
    summary="Добавить событие получения от отправителя",
    status_code=status.HTTP_201_CREATED,
)
async def add_pickup(
    data: PickupCreateSchema,
    context: dict = Depends(require_permission_in_context("add_pickup")),
):
    await validate_exists(Parcel, data.parcel_id, "Накладная")
    pickup = await Pickup.create(created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump())
    if data.warehouse_id:
        await ParcelStatus.create(
            parcel_id=data.parcel_id,
            document_id=pickup.id,
            document_type="pickup_id",
            status=ParcelStatusEnum.ON_WAREHOUSE,
            date=data.date,
            value=data.warehouse_id,
            value_type="warehouse_id",
            created_by=context["user_id"],
        )
    else:
        await ParcelStatus.create(
            parcel_id=data.parcel_id,
            document_id=pickup.id,
            document_type="pickup_id",
            status=ParcelStatusEnum.WITH_EMPLOYEE,
            date=data.date,
            value=data.employee_id,
            value_type="user_id",
            created_by=context["user_id"],
        )
    await recalculate_parcel_status(data.parcel_id)
    return PickupResponseSchema(pickup_id=pickup.id)


@pickup_router.get(
    "/all",
    response_model=PickupListResponseSchema,
    summary="Получение списка событий получения от отправителя",
)
async def get_pickup_list(
    filters: dict = Depends(pickup_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_pickups")),
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

    if filters.get("parcel_name"):
        query &= Q(parcel__name__icontains=filters["parcel_name"])

    sort_by = filters.get("sort_by", "date")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await Pickup.filter(query).count()
    pickups = await Pickup.filter(query).prefetch_related("parcel").order_by(sort_field).offset(offset).limit(page_size)

    pickups_data = [
        PickupSchema.model_validate(
            {
                **pickup.__dict__,
                "pickup_id": pickup.id,
                "parcel_name": pickup.parcel.name if pickup.parcel else None,
            },
            from_attributes=True,
        )
        for pickup in pickups
    ]
    return PickupListResponseSchema(
        total=total_count,
        pickups=pickups_data,
    )


@pickup_router.get(
    "/{pickup_id}",
    response_model=PickupSchema,
    summary="Просмотр одного события получения от отправителя",
)
async def get_pickup(
    pickup_id: UUID,
    _: dict = Depends(require_permission_in_context("view_pickup")),
):
    pickup = await Pickup.filter(id=pickup_id).first()

    if not pickup:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    return PickupSchema.model_validate(pickup, from_attributes=True)


@pickup_router.patch(
    "/{pickup_id}",
    response_model=PickupResponseSchema,
    summary="Редактирование события получения от отправителя",
)
async def edit_pickup(
    pickup_id: UUID,
    data: PickupEditSchema,
    context: dict = Depends(require_permission_in_context("edit_pickup")),
):
    pickup = await Pickup.filter(id=pickup_id).prefetch_related("parcel").first()

    if not pickup:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    await pickup.update_from_dict(data.model_dump(exclude_unset=True))
    pickup.modified_by = context["user_id"]
    await pickup.save()
    await ParcelStatus.filter(document_id=pickup_id).delete()
    if pickup.warehouse_id:
        await ParcelStatus.create(
            parcel_id=pickup.parcel.id,
            document_id=pickup.id,
            document_type="pickup_id",
            status=ParcelStatusEnum.ON_WAREHOUSE,
            date=pickup.date,
            value=pickup.warehouse_id,
            value_type="warehouse_id",
            created_by=context["user_id"],
        )
    else:
        await ParcelStatus.create(
            parcel_id=pickup.parcel.id,
            document_id=pickup.id,
            document_type="pickup_id",
            status=ParcelStatusEnum.WITH_EMPLOYEE,
            date=pickup.date,
            value=pickup.employee_id,
            value_type="user_id",
            created_by=context["user_id"],
        )

    await recalculate_parcel_status(pickup.parcel.id)

    return PickupResponseSchema(pickup_id=pickup.id)


@pickup_router.delete(
    "/{pickup_id}",
    summary="Удаление события получения от отправителя",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_pickup(
    pickup_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_pickup")),
):
    pickup = await Pickup.filter(id=pickup_id).prefetch_related("parcel").first()

    if not pickup:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    await ParcelStatus.filter(document_id=pickup_id).delete()
    await recalculate_parcel_status(pickup.parcel.id)
    await pickup.delete()
    return
