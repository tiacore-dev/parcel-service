# app/handlers/service_updater.py
from __future__ import annotations

import asyncio
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from loguru import logger
from tiacore_lib.http.http_client import SharedHttpClient, get_auth_headers

from app.database.models import Parcel, Service

http = SharedHttpClient()


def calc_base_value_dec(parcel: Parcel) -> Decimal:
    w = Decimal(str(parcel.weight or 0))
    v = Decimal(str(parcel.volume or 0))
    b = max(w, v * Decimal("200"))
    return b.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)  # под PriceDetail.*(…,3)


async def recompute_services_for_parcel(
    settings, request, parcel_id: UUID, modified_by: Optional[UUID] = None
) -> Dict[str, Any]:
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        return {"updated_base": 0, "priced": 0}

    base_value = calc_base_value_dec(parcel)

    # 1) Проставим base_value всем услугам (уже DecimalField(10,3))
    updated_base = await Service.filter(parcel_id=parcel_id).update(
        base_value=base_value,  # Tortoise сам приведёт Decimal -> DB numeric
        modified_by=modified_by,
    )

    services = await Service.filter(parcel_id=parcel_id)
    price_ids = {s.price_id for s in services if s.price_id}

    # 2) Квотируем суммы по уникальным price_id
    if not price_ids:
        return {"updated_base": updated_base, "priced": 0}

    price_url = getattr(settings, "PRICE_URL", None)
    if not price_url or not str(price_url).lower().startswith(("http://", "https://")):
        logger.warning("[pricing] PRICE_URL is empty/invalid, skip quoting")
        return {"updated_base": updated_base, "priced": 0}

    headers = get_auth_headers(request)

    async def quote_one(pid):
        url = f"{price_url}/api/calculate/{pid}"
        data, status = await http.request("POST", url, headers=headers, json={"base_value": str(base_value)})
        if status == 200 and isinstance(data, dict) and "summ" in data:
            try:
                amt = Decimal(str(data["summ"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                return pid, amt
            except Exception:
                logger.warning(f"[pricing] bad 'summ' for price_id={pid}: {data!r}")
        else:
            logger.warning(f"[pricing] quote failed for price_id={pid}: status={status}, data={data!r}")
        return pid, None

    results = await asyncio.gather(*(quote_one(pid) for pid in price_ids))

    priced = 0
    for pid, amount in results:
        if amount is None:
            continue
        priced += await Service.filter(parcel_id=parcel_id, price_id=pid).update(
            summ=amount,  # Decimal -> DB numeric(12,2)
            modified_by=modified_by,
        )
    return {"updated_base": updated_base, "priced": priced}
