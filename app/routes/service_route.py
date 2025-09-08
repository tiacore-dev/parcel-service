from uuid import UUID

# service_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from tiacore_lib.config import get_settings
from tiacore_lib.handlers.dependency_handler import require_permission_in_context
from tortoise.expressions import Q

from app.database.models import Parcel, Service
from app.handlers.get_redis import get_redis
from app.handlers.parcel_scope_updater import recalc_parcel_scope_from_services, reprice_and_recalc_scope_for_parcel
from app.handlers.pricing_helpers import compute_base_value_for_service, fetch_price_id_for_service
from app.handlers.scope_handler import add_companies_with_index
from app.pydantic_models.service_models import (
    ServiceCreateSchema,
    ServiceEditSchema,
    ServiceListResponseSchema,
    ServiceResponseSchema,
    ServiceSchema,
    service_filter_params,
)

service_router = APIRouter()


@service_router.post(
    "/add",
    response_model=ServiceResponseSchema,
    summary="Добавить услугу",
    status_code=status.HTTP_201_CREATED,
)
async def add_service(
    request: Request,
    data: ServiceCreateSchema,
    context: dict = Depends(require_permission_in_context("add_service")),
    settings=Depends(get_settings),
    redis_client=Depends(get_redis),
):
    parcel = await Parcel.get_or_none(id=data.parcel_id)
    if not parcel:
        raise HTTPException(status_code=400, detail="Накладная не найдена")

    # 1) считаем base_value
    base_value = compute_base_value_for_service(parcel, data.service_type)

    # 2) подбираем price_id по контракту/маршруту
    # контракт берём из data.contract_id (у сервиса свой контракт)
    price_id, company_ids = await fetch_price_id_for_service(
        request=request, settings=settings, service_type=data.service_type, parcel=parcel, contract_id=data.contract_id
    )

    # 3) создаём услугу
    service = await Service.create(
        created_by=context["user_id"],
        modified_by=context["user_id"],
        service_type=data.service_type,
        contract_id=data.contract_id,
        price_id=price_id,
        parcel_id=data.parcel_id,
        base_value=base_value,
        # summ не задаём — посчитается в repricer-е
    )

    # (опционально) расширить видимость накладной доп. компаниями тарифа
    if company_ids:
        await add_companies_with_index(redis_client, parcel.id, company_ids)

    # 4) репрайсим все услуги накладной и пересобираем scope
    await reprice_and_recalc_scope_for_parcel(
        request,
        settings,
        redis_client,
        parcel_id=service.parcel_id,  # type: ignore
        modified_by=context["user_id"],
    )

    return ServiceResponseSchema(service_id=service.id)


@service_router.patch(
    "/{service_id}",
    response_model=ServiceResponseSchema,
    summary="Редактирование услуги",
)
async def edit_service(
    service_id: UUID,
    data: ServiceEditSchema,
    request: Request,
    context: dict = Depends(require_permission_in_context("edit_service")),
    settings=Depends(get_settings),
    redis_client=Depends(get_redis),
):
    service = await Service.get_or_none(id=service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")

    old_parcel_id = service.parcel_id  # type: ignore

    # применяем «простые» изменения (без вычисляемых полей)
    await service.update_from_dict(data.model_dump(exclude_unset=True))
    # нужно актуальный parcel для перерасчётов
    parcel = await Parcel.get_or_none(id=service.parcel_id)  # type: ignore
    if not parcel:
        raise HTTPException(status_code=400, detail="Накладная не найдена")

    # 1) пересчитать base_value
    service.base_value = compute_base_value_for_service(parcel, service.service_type)  # type: ignore

    # 2) при изменении service_type/contract_id/маршрута — перебрать price_id
    price_id, company_ids = await fetch_price_id_for_service(
        request=request,
        settings=settings,
        service_type=service.service_type,
        parcel=parcel,  # type: ignore
        contract_id=data.contract_id if data.contract_id else service.contract_id,
    )
    service.price_id = price_id

    service.modified_by = context["user_id"]
    await service.save()

    if company_ids:
        await add_companies_with_index(redis_client, parcel.id, company_ids)

    # если переехала на другую накладную — пересчитать обе
    new_parcel_id = service.parcel_id  # type: ignore
    if new_parcel_id != old_parcel_id:
        await reprice_and_recalc_scope_for_parcel(
            request, settings, redis_client, parcel_id=old_parcel_id, modified_by=context["user_id"]
        )

    await reprice_and_recalc_scope_for_parcel(
        request, settings, redis_client, parcel_id=new_parcel_id, modified_by=context["user_id"]
    )

    return ServiceResponseSchema(service_id=service.id)


@service_router.delete(
    "/{service_id}",
    summary="Удаление услуги",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service(
    service_id: UUID,
    request: Request,
    _: dict = Depends(require_permission_in_context("delete_service")),
    settings=Depends(get_settings),
    redis_client=Depends(get_redis),
):
    service = await Service.filter(id=service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")

    parcel_id = service.parcel_id  # type: ignore
    await service.delete()

    # пересчёт после удаления
    await recalc_parcel_scope_from_services(request, settings, redis_client, parcel_id)


@service_router.get(
    "/all",
    response_model=ServiceListResponseSchema,
    summary="Получение услуг",
)
async def get_service_list(
    filters: dict = Depends(service_filter_params),
    _: dict = Depends(require_permission_in_context("get_all_services")),
):
    query = Q()

    if filters.get("parcel_id"):
        query &= Q(parcel_id=filters["parcel_id"])

    if filters.get("service_type"):
        query &= Q(service_type=filters["service_type"])

    if filters.get("contract_id"):
        query &= Q(contract_id=filters["contract_id"])

    if filters.get("price_id"):
        query &= Q(price_id=filters["price_id"])

    sort_by = filters.get("sort_by", "created_at")
    order = filters.get("order", "asc").lower()
    sort_field = sort_by if order == "asc" else f"-{sort_by}"
    page = filters.get("page", 1)
    page_size = filters.get("page_size", 10)
    offset = (page - 1) * page_size

    total_count = await Service.filter(query).count()
    services = await Service.filter(query).order_by(sort_field).offset(offset).limit(page_size)

    return ServiceListResponseSchema(
        total=total_count,
        services=[ServiceSchema.model_validate(service) for service in services],
    )


@service_router.get(
    "/{service_id}",
    response_model=ServiceSchema,
    summary="Просмотр одной услуги",
)
async def get_service(
    service_id: UUID,
    _: dict = Depends(require_permission_in_context("view_service")),
):
    service = await Service.filter(id=service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")

    return ServiceSchema.model_validate(service, from_attributes=True)
