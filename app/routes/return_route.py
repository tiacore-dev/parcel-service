from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import ParcelStatus, ParcelStatusEnum, Return, ReturnDetails
from app.handlers.status_handler import recalculate_parcel_status
from app.pydantic_models.return_models import (
    ReturnCreateBulkSchema,
    ReturnCreateSchema,
    ReturnEditSchema,
    ReturnListResponseSchema,
    ReturnResponseSchema,
    ReturnSchema,
    return_filter_params,
)

return_router = APIRouter()


@return_router.post(
    "/add",
    response_model=ReturnResponseSchema,
    summary="Добавить событие возврата отправителю",
    status_code=status.HTTP_201_CREATED,
)
async def add_return(
    data: ReturnCreateSchema,
    context: dict = Depends(require_permission_in_context("add_return")),
):
    return_obj = await Return.create(created_by=context["user_id"], modified_by=context["user_id"], **data.model_dump())

    return ReturnResponseSchema(return_id=return_obj.id)


@return_router.post(
    "/add-bulk",
    response_model=ReturnResponseSchema,
    summary="Добавить возврат",
    status_code=status.HTTP_201_CREATED,
)
async def add_bulk_return(
    data: ReturnCreateBulkSchema,
    context: dict = Depends(require_permission_in_context("add_return_bulk")),
):
    create_data = data.model_dump()
    parcel_ids = create_data["parcels"]
    create_data.pop("parcels")
    return_obj = await Return.create(created_by=context["user_id"], modified_by=context["user_id"], **create_data)
    await ReturnDetails.bulk_create(
        [
            ReturnDetails(
                created_by=context["user_id"], modified_by=context["user_id"], parcel_id=parcel, returns=return_obj
            )
            for parcel in data.parcels
        ]
    )
    for parcel_id in parcel_ids:
        await ParcelStatus.create(
            parcel_id=parcel_id,
            document_id=return_obj.id,
            document_type="return_id",
            status=ParcelStatusEnum.RETURNED,
            date=return_obj.date,
            created_by=context["user_id"],
        )
        await recalculate_parcel_status(parcel_id)
    return ReturnResponseSchema(return_id=return_obj.id)


@return_router.get(
    "/all",
    response_model=ReturnListResponseSchema,
    summary="Получение списка возвратов отправителю",
)
async def get_return_list(
    filters: dict = Depends(return_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_returns")),
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

    if filters.get("returns_id"):
        query &= Q(returns_id=filters["returns_id"])

    if filters.get("sender_name"):
        query &= Q(sender_name__icontains=filters["sender_name"])

    sort_by = filters.get("sort_by", "date")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await Return.filter(query).count()
    returns = await Return.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return_schemas = []
    for return_obj in returns:
        parcels = []

        for detail in await return_obj.return_details.all():
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

        return_dict = return_obj.__dict__.copy()

        return_dict["parcel_count"] = len(parcels)
        return_dict["parcels"] = parcels

        return_schemas.append(ReturnSchema.model_validate(return_dict, from_attributes=True))

    return ReturnListResponseSchema(
        total=total_count,
        returns=return_schemas,
    )


@return_router.get(
    "/{return_id}",
    response_model=ReturnSchema,
    summary="Просмотр одного события возврата отправителю",
)
async def get_return(
    return_id: UUID,
    _: dict = Depends(require_permission_in_context("view_return")),
):
    return_obj = await Return.filter(id=return_id).first()

    if not return_obj:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    return ReturnSchema.model_validate(return_obj, from_attributes=True)


@return_router.patch(
    "/{return_id}",
    response_model=ReturnResponseSchema,
    summary="Редактирование события возврата отправителю",
)
async def edit_return(
    return_id: UUID,
    data: ReturnEditSchema,
    context: dict = Depends(require_permission_in_context("edit_return")),
):
    return_obj = await Return.filter(id=return_id).first()

    if not return_obj:
        raise HTTPException(status_code=404, detail="Событие не найдено")

    await return_obj.update_from_dict(data.model_dump(exclude_unset=True))
    return_obj.modified_by = context["user_id"]
    await return_obj.save()

    return ReturnResponseSchema(return_id=return_obj.id)


@return_router.delete(
    "/{return_id}",
    summary="Удаление события возврата отправителю",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_return(
    return_id: UUID,
    _: dict = Depends(require_permission_in_context("delete_return")),
):
    return_obj = await Return.filter(id=return_id).first()

    if not return_obj:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    await ParcelStatus.filter(document_id=return_id).delete()
    await return_obj.delete()
    return
