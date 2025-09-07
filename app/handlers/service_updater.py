from __future__ import annotations

import asyncio
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional
from uuid import UUID

from loguru import logger
from tiacore_lib.http.http_client import SharedHttpClient, get_auth_headers

from app.database.models import Parcel, Service

http_client = SharedHttpClient()


def _calc_base_value_decimal(parcel: Parcel) -> Decimal:
    w = Decimal(str(parcel.weight or 0))
    v = Decimal(str(parcel.volume or 0))
    return max(w, v * Decimal("200"))


def _valid_base_url(url: str | None) -> bool:
    if not url:
        return False
    s = url.strip().lower()
    return s.startswith("http://") or s.startswith("https://")


async def recompute_services_for_parcel(
    settings,
    request,
    parcel_id: UUID,
    modified_by: Optional[UUID] = None,
    *,
    concurrency: int = 8,
) -> dict:
    """
    1) Пересчитывает base_value для всех услуг накладной.
    2) Считает summ по price-service для каждой уникальной пары (price_id, base_value).
    Возвращает {"updated_base": int, "priced": int}.
    """
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        return {"updated_base": 0, "priced": 0}

    base_value_dec = _calc_base_value_decimal(parcel)

    # 1) Массово проставим base_value всем услугам этой накладной
    updated_base = await Service.filter(parcel_id=parcel_id).update(
        base_value=float(base_value_dec),  # поле FloatField
        modified_by=modified_by,
    )

    # Соберём услуги (для квоты нужны только id и price_id)
    services = await Service.filter(parcel_id=parcel_id)
    price_ids = {s.price_id for s in services if s.price_id}

    if not price_ids:
        return {"updated_base": updated_base, "priced": 0}

    if not _valid_base_url(getattr(settings, "PRICE_URL", None)):
        logger.warning("[pricing] PRICE_URL is empty or invalid, skip quoting")
        return {"updated_base": updated_base, "priced": 0}

    headers = get_auth_headers(request)
    sem = asyncio.Semaphore(concurrency)

    async def _quote_one(price_id: UUID):
        url = f"{settings.PRICE_URL}/api/prices/{price_id}/quote"  # <— см. маршрут в price-service
        payload = {"base_value": str(base_value_dec)}  # Decimal → str без потери точности
        async with sem:
            data, status_code = await http_client.request("POST", url, headers=headers, json=payload)
        if status_code == 200 and isinstance(data, dict) and "summ" in data:
            try:
                # округлим до 2 знаков (как деньги)
                amount = Decimal(str(data["summ"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                return price_id, amount
            except Exception:
                logger.warning(f"[pricing] bad 'summ' format for price_id={price_id}: {data!r}")
        else:
            logger.warning(f"[pricing] quote failed for price_id={price_id}: status={status_code}, data={data!r}")
        return price_id, None

    # 2) Считаем квоты для каждого уникального price_id
    results = await asyncio.gather(*(_quote_one(pid) for pid in price_ids))

    # 3) Массово проставим summ по группам price_id (не затирая, если квота не получилась)
    priced_total = 0
    for pid, amount in results:
        if amount is None:
            continue
        # одна операция UPDATE на все услуги этой накладной с данным price_id
        priced_total += await Service.filter(parcel_id=parcel_id, price_id=pid).update(
            summ=float(amount),  # FloatField
            modified_by=modified_by,
        )

    return {"updated_base": updated_base, "priced": priced_total}
