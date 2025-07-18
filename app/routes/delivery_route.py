from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.utils.validate_helpers import validate_exists
from tortoise.expressions import Q

from app.database.models import (
    Delivery,
    Parcel,
    ParcelStatus,
    ParcelStatusEnum,
)
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.delivery_models import (
    DeliveryCreateSchema,
    DeliveryEditSchema,
    DeliveryListResponseSchema,
    DeliveryResponseSchema,
    DeliverySchema,
    delivery_filter_params,
)

delivery_router = APIRouter()


@delivery_router.post(
    "/add",
    response_model=DeliveryResponseSchema,
    summary="Добавить событие доставки получателю",
    status_code=status.HTTP_201_CREATED,
)
async def add_delivery(
    data: DeliveryCreateSchema,
    context: dict = Depends(require_permission_in_context("add_delivery")),
):
    await validate_exists(Parcel, data.parcel_id, "Накладная")
    delivery = await Delivery.create(created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump())
    await ParcelStatus.create(
        parcel_id=data.parcel_id,
        document_id=delivery.id,
        document_type="delivery_id",
        status=ParcelStatusEnum.DELIVERED,
        date=data.date,
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(data.parcel_id)
    return DeliveryResponseSchema(delivery_id=delivery.id)


@delivery_router.get(
    "/all",
    response_model=DeliveryListResponseSchema,
    summary="Получение списка событий доставки получателю",
)
async def get_delivery_list(
    filters: dict = Depends(delivery_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_deliveries")),
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

    if filters.get("recipient_name"):
        query &= Q(recipient_name__icontains=filters["recipient_name"])

    if filters.get("parcel_name"):
        query &= Q(parcel__name__icontains=filters["parcel_name"])

    sort_by = filters.get("sort_by", "date")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await Delivery.filter(query).count()
    deliveries = (
        await Delivery.filter(query).prefetch_related("parcel").order_by(sort_field).offset(offset).limit(page_size)
    )

    delivery_data = [
        DeliverySchema.model_validate(
            {
                **delivery.__dict__,
                "delivery_id": delivery.id,
                "parcel_name": delivery.parcel.name if delivery.parcel else None,
            },
            from_attributes=True,
        )
        for delivery in deliveries
    ]
    return DeliveryListResponseSchema(
        total=total_count,
        deliveries=delivery_data,
    )


@delivery_router.get(
    "/{delivery_id}",
    response_model=DeliverySchema,
    summary="Просмотр одного события доставки получателю",
)
async def get_delivery(
    delivery_id: UUID,
    _: dict = Depends(require_permission_in_context("view_delivery")),
):
    delivery = await Delivery.filter(id=delivery_id).first()

    if not delivery:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    return DeliverySchema.model_validate(delivery, from_attributes=True)


@delivery_router.patch(
    "/{delivery_id}",
    response_model=DeliveryResponseSchema,
    summary="Редактирование события доставки получателю",
)
async def edit_delivery(
    delivery_id: UUID,
    data: DeliveryEditSchema,
    context: dict = Depends(require_permission_in_context("edit_delivery")),
):
    delivery = await Delivery.filter(id=delivery_id).prefetch_related("parcel").first()

    if not delivery:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    await delivery.update_from_dict(data.model_dump(exclude_unset=True))
    delivery.modified_by = context["user_id"]
    await delivery.save()
    await ParcelStatus.filter(document_id=delivery_id).delete()
    await ParcelStatus.create(
        parcel_id=delivery.parcel.id,
        document_id=delivery.id,
        document_type="delivery_id",
        status=ParcelStatusEnum.DELIVERED,
        date=delivery.date,
        created_by=context["user_id"],
    )
    await recalculate_parcel_status(delivery.parcel.id)

    return DeliveryResponseSchema(delivery_id=delivery.id)


@delivery_router.delete(
    "/{delivery_id}",
    summary="Удаление события доставки получателю",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_delivery(
    delivery_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_delivery")),
):
    delivery = await Delivery.filter(id=delivery_id).prefetch_related("parcel").first()

    if not delivery:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    await ParcelStatus.filter(document_id=delivery_id).delete()
    await recalculate_parcel_status(delivery.parcel.id)
    await delivery.delete()
    return
