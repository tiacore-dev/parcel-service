from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from loguru import logger
from tiacore_lib.config import get_settings
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tiacore_lib.handlers.permissions_handler import with_permission_and_company_from_body_check
from tiacore_lib.http.http_client import (
    SharedHttpClient,
    get_auth_headers,
)

# from tiacore_lib.utils.validate_helpers import validate_company_access
from tortoise.expressions import Q

from app.database.models import Parcel, Service, ServiceType
from app.handlers.status_handler import get_cached_parcel_status_data
from app.pydantic_models.get_ids_models import GetPriceIDSchema
from app.pydantic_models.parcel_models import (
    ParcelAllSchema,
    ParcelCreateSchema,
    ParcelCurrentStatusSchema,
    ParcelEditSchema,
    ParcelListResponseSchema,
    ParcelResponseSchema,
    ParcelSchema,
    ParcelViewSchema,
    parcel_filter_params,
)
from app.utils.db_helpers import generate_parcel_name

parcel_router = APIRouter()
http_client = SharedHttpClient()


@parcel_router.post(
    "/add",
    response_model=ParcelResponseSchema,
    summary="Добавить накладную",
    status_code=status.HTTP_201_CREATED,
)
async def add_parcel(
    request: Request,
    data: ParcelCreateSchema,
    context=Depends(with_permission_and_company_from_body_check("add_parcel")),
    settings=Depends(get_settings),
):
    create_data = data.model_dump()
    if not data.name:
        create_data["name"] = await generate_parcel_name()
    parcel = await Parcel.create(created_by=context["user_id"], modified_by=context["user_id"], **create_data)

    headers = get_auth_headers(request)
    json_data = GetPriceIDSchema(
        service_type=ServiceType.STANDARD,
        sender_city_id=data.sender_city,
        recipient_city_id=data.recipient_city,
        sender_warehouse_id=data.sender_warehouse,
        recipient_warehouse_id=data.recipient_warehouse,
    )

    response_data, status_code = await http_client.request(
        "POST",
        f"{settings.CONTRACT_URL}/api/get-company-ids/{data.contract_id}",
        headers=headers,
        json=json_data.model_dump(mode="json"),
    )
    logger.debug(f"Response from contracts-service: {response_data}, status={status_code}")
    if status_code == 200:
        await Service.create(
            created_by=context["user_id"],
            modified_by=context["user_id"],
            parcel=parcel,
            contract_id=data.contract_id,
            base_value=0,
            summ=0,
            service_type=ServiceType.STANDARD,
            price_id=response_data["price_id"],
        )
    return ParcelResponseSchema(parcel_id=parcel.id)


@parcel_router.patch(
    "/{parcel_id}",
    response_model=ParcelResponseSchema,
    summary="Изменение накладной",
)
async def edit_parcel(
    parcel_id: UUID,
    data: ParcelEditSchema,
    context: dict = Depends(require_permission_in_context("delete_parcel")),
):
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="")
    # validate_company_access(parcel, context, "Накладная")
    await parcel.update_from_dict(data.model_dump(exclude_unset=True))
    parcel.modified_by = context["user_id"]
    await parcel.save()

    return ParcelResponseSchema(parcel_id=parcel.id)


@parcel_router.delete(
    "/{parcel_id}",
    summary="Удаление накладной",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_parcel(
    parcel_id: UUID,
    context: dict = Depends(require_permission_in_context("delete_parcel")),
):
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="")
    # validate_company_access(parcel, context, "Накладная")
    await parcel.delete()


@parcel_router.get(
    "/all",
    response_model=ParcelListResponseSchema,
    summary="Получение списка накладных",
)
async def get_parcels(
    filters: dict = Depends(parcel_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_parcels")),
):
    query = Q()

    if filters.get("sender_city"):
        query &= Q(sender_city=filters["sender_city"])

    if filters.get("recipient_city"):
        query &= Q(recipient_city=filters["recipient_city"])

    if filters.get("pickup_date_from"):
        query &= Q(pickup_estimated_date__gte=filters["pickup_date_from"])

    if filters.get("pickup_date_to"):
        query &= Q(pickup_estimated_date__lte=filters["pickup_date_to"])

    if filters.get("search"):
        search = filters["search"]
        query &= (
            Q(sender_address__icontains=search)
            | Q(recipient_address__icontains=search)
            | Q(sender_company__icontains=search)
            | Q(recipient_company__icontains=search)
            | Q(sender_phone__icontains=search)
            | Q(recipient_phone__icontains=search)
            | Q(sender_email__icontains=search)
            | Q(recipient_email__icontains=search)
            | Q(sender_telegram__icontains=search)
            | Q(recipient_telegram__icontains=search)
            | Q(note__icontains=search)
            | Q(name__icontains=search)
        )

    sort_by = filters.get("sort_by", "created_at")
    if sort_by == "parcel_name":
        sort_by = "name"
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await Parcel.filter(query).count()
    parcels = await Parcel.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    parcel_schemas = []
    for parcel in parcels:
        status_data = await get_cached_parcel_status_data(parcel.id)
        status = status_data["status"] if status_data else None

        parcel_dict = ParcelSchema.model_validate(parcel).model_dump()

        parcel_schemas.append(ParcelAllSchema(**parcel_dict, status=status))

    return ParcelListResponseSchema(total=total_count, parcels=parcel_schemas)


@parcel_router.get(
    "/{parcel_id}/status",
    response_model=Optional[ParcelCurrentStatusSchema],
    summary="Получение актуального статуса накладной",
)
async def get_parcel_status(
    parcel_id: UUID,
    _: dict = Depends(require_permission_in_context("get_parcel_current_status")),
):
    data = await get_cached_parcel_status_data(parcel_id=parcel_id)
    if not data:
        return None

    return ParcelCurrentStatusSchema.model_validate(data)


@parcel_router.get(
    "/by-number",
    response_model=ParcelViewSchema,
    summary="Просмотр одной накладной",
)
async def get_parcel_by_number(
    parcel_name: str = Query(..., description="Номер накладной"),
    context: dict = Depends(require_permission_in_context("view_parcel")),
):
    parcel = await Parcel.filter(name=parcel_name).first()

    if not parcel:
        raise HTTPException(status_code=404, detail="Накладная не найдена")
    # validate_company_access(parcel, context, "Накладная")
    status_data = await get_cached_parcel_status_data(parcel.id)
    return ParcelViewSchema(
        **ParcelSchema.model_validate(parcel, from_attributes=True).model_dump(),
        status=ParcelCurrentStatusSchema.model_validate(status_data) if status_data else None,
    )


@parcel_router.get(
    "/{parcel_id}",
    response_model=ParcelViewSchema,
    summary="Просмотр одной накладной",
)
async def get_legal_parcel(
    parcel_id: UUID,
    context: dict = Depends(require_permission_in_context("view_parcel")),
):
    parcel = await Parcel.filter(id=parcel_id).first()

    if not parcel:
        raise HTTPException(status_code=404, detail="Накладная не найдена")
    # validate_company_access(parcel, context, "Накладная")
    status_data = await get_cached_parcel_status_data(parcel.id)
    return ParcelViewSchema(
        **ParcelSchema.model_validate(parcel, from_attributes=True).model_dump(),
        status=ParcelCurrentStatusSchema.model_validate(status_data) if status_data else None,
    )
