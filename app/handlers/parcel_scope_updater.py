# app/handlers/parcel_scope_updater.py
from __future__ import annotations

from typing import Iterable, Optional, Set
from uuid import UUID

from fastapi import Request
from loguru import logger
from tiacore_lib.http.http_client import SharedHttpClient, get_auth_headers

from app.database.models import Parcel, Service
from app.handlers.scope_handler import set_parcel_scope_with_index  # или scope_store
from app.pydantic_models.get_ids_models import GetPriceIDSchema

# ^^^ проверь имя модуля: у тебя импортируется scope_handler

http_client = SharedHttpClient()


http_client = SharedHttpClient()


async def _fetch_service_companies_and_price(
    request: Request,
    settings,
    *,
    service: Service,
    parcel: Parcel,
) -> tuple[Set[UUID], Optional[UUID]]:
    """
    Возвращает (множество company_ids, новый price_id | None) по данным contract-service.
    """
    headers = get_auth_headers(request)
    payload = GetPriceIDSchema(
        service_type=service.service_type,
        sender_city_id=parcel.sender_city,
        recipient_city_id=parcel.recipient_city,
        sender_warehouse_id=parcel.sender_warehouse,
        recipient_warehouse_id=parcel.recipient_warehouse,
    )
    url = f"{settings.CONTRACT_URL}/api/get-company-ids/{service.contract_id}"

    data, status_code = await http_client.request("POST", url, headers=headers, json=payload.model_dump(mode="json"))
    if status_code != 200 or not isinstance(data, dict):
        logger.warning(
            f"[scope] contract-service failed for service={service.id}, "
            f"parcel={parcel.id}: status={status_code}, data={data!r}"
        )
        return set(), None

    companies: set[UUID] = set()
    for k in ("buyer_company_ids", "seller_company_ids"):
        for raw in data.get(k) or []:
            try:
                companies.add(raw if isinstance(raw, UUID) else UUID(str(raw)))
            except Exception:
                pass

    price_id = None
    if "price_id" in data and data["price_id"]:
        try:
            price_id = data["price_id"] if isinstance(data["price_id"], UUID) else UUID(str(data["price_id"]))
        except Exception:
            logger.warning(f"[scope] bad price_id for service={service.id}: {data.get('price_id')!r}")

    return companies, price_id


async def reprice_and_recalc_scope_for_parcel(
    request: Request,
    settings,
    redis_client,
    *,
    parcel_id: UUID,
    modified_by: Optional[UUID] = None,
) -> None:
    """
    Для указанной накладной:
    1) для каждой услуги — получаем компании и (возможно) новый price_id, обновляем услугу;
    2) пересобираем parcel->companies и обратный индекс (company->parcels) в Redis.
    """
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        return

    services = await Service.filter(parcel_id=parcel_id)
    union_companies: set[UUID] = set()
    dirty: list[Service] = []

    for s in services:
        companies, new_price_id = await _fetch_service_companies_and_price(request, settings, service=s, parcel=parcel)
        union_companies |= companies

        if new_price_id and getattr(s, "price_id", None) != new_price_id:
            s.price_id = new_price_id
            if modified_by is not None and hasattr(s, "modified_by"):
                s.modified_by = modified_by
            dirty.append(s)

    if dirty:
        # обновим только price_id (+ modified_by, если есть)
        fields = ["price_id"]
        if modified_by is not None and hasattr(services[0], "modified_by"):
            fields.append("modified_by")
        await Service.bulk_update(dirty, fields=fields)

    # даже если часть запросов упала — зафиксируем то, что удалось собрать
    await set_parcel_scope_with_index(redis_client, parcel_id, union_companies)


def _as_uuid_set(items: Iterable[UUID | str]) -> set[UUID]:
    out: set[UUID] = set()
    for x in items or []:
        try:
            out.add(x if isinstance(x, UUID) else UUID(str(x)))
        except Exception:
            pass
    return out


async def _resolve_companies_for_service(
    request: Request,
    settings,
    service: Service,
    parcel: Parcel,
) -> set[UUID]:
    """
    Берём компании из contract-service. Используем тот же эндпоинт, что в add_parcel,
    но подставляем маршрут из Parcel и тип услуги из Service.
    """
    headers = get_auth_headers(request)
    payload = GetPriceIDSchema(
        service_type=service.service_type,
        sender_city_id=parcel.sender_city,
        recipient_city_id=parcel.recipient_city,
        sender_warehouse_id=parcel.sender_warehouse,
        recipient_warehouse_id=parcel.recipient_warehouse,
    )

    url = f"{settings.CONTRACT_URL}/api/get-company-ids/{service.contract_id}"
    data, status_code = await http_client.request(
        "POST",
        url,
        headers=headers,
        json=payload.model_dump(mode="json"),
    )
    if status_code != 200 or not isinstance(data, dict):
        logger.warning(
            f"[scope] cannot resolve companies for service {service.id} "
            f"(parcel={parcel.id}): status={status_code}, data={data!r}"
        )
        return set()

    companies = set()
    companies |= _as_uuid_set(data.get("buyer_company_ids") or [])
    companies |= _as_uuid_set(data.get("seller_company_ids") or [])
    return companies


async def recalc_parcel_scope_from_services(
    request: Request,
    settings,
    redis_client,
    parcel_id: UUID,
) -> None:
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        return

    services = await Service.filter(parcel_id=parcel_id)
    company_ids: set[UUID] = set()
    for s in services:
        company_ids |= await _resolve_companies_for_service(request, settings, s, parcel)

    await set_parcel_scope_with_index(redis_client, parcel_id, company_ids)
