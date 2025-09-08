# app/handlers/pricing_helpers.py
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, Request

from app.database.models import Parcel, ServiceType
from app.pydantic_models.get_ids_models import GetPriceIDSchema


def compute_base_value_for_service(parcel: Parcel, service_type: ServiceType) -> float:
    """
    Базовое правило: для весо-габаритных услуг берём max(weight, volume*200).
    При необходимости сюда легко добавить особые кейсы по service_type.
    """
    # TODO: при необходимости развести математику по типам услуг
    weight = Decimal(parcel.weight or 0)
    volume = Decimal(parcel.volume or 0)
    return float(max(weight, volume * Decimal("200")))


async def fetch_price_id_for_service(
    request: Request, settings, service_type: ServiceType, parcel: Parcel
) -> tuple[UUID, list[UUID]]:
    """
    Получаем price_id через CONTRACT_URL так же, как в создании накладной.
    Возвращаем (price_id, company_ids_for_visibility)
    """
    from tiacore_lib.http.http_client import SharedHttpClient, get_auth_headers

    http_client = SharedHttpClient()

    payload = GetPriceIDSchema(
        service_type=service_type,
        sender_city_id=parcel.sender_city,
        recipient_city_id=parcel.recipient_city,
        sender_warehouse_id=parcel.sender_warehouse,
        recipient_warehouse_id=parcel.recipient_warehouse,
    )
    headers = get_auth_headers(request)

    response_data, status_code = await http_client.request(
        "POST",
        f"{settings.CONTRACT_URL}/api/get-company-ids/{
            parcel.contract_id if hasattr(parcel, 'contract_id') else None or ''  # type: ignore
        }",
        headers=headers,
        json=payload.model_dump(mode="json"),
    )
    if status_code != 200:
        raise HTTPException(400, detail="Не удалось подобрать тариф (price_id) для услуги")

    # Собираем компании для видимости (если нужно)
    buyer = response_data.get("buyer_company_ids") or []
    seller = response_data.get("seller_company_ids") or []
    company_ids = [UUID(str(x)) for x in [*buyer, *seller]]
    return response_data["price_id"], company_ids
