from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest

from app.database.models import DeliveryType, Parcel, Service


@pytest.fixture
async def seed_parcel(seed_company, seed_user):
    now = datetime.now()
    time_from = now.time()
    time_to = (now + timedelta(hours=2)).time()  # например, +2 часа

    parcel = await Parcel.create(
        company_id=seed_company,
        name="00001",
        sender_city=uuid4(),
        sender_address="ул. Тестовая, д.1",
        sender_delivery_type=DeliveryType.DOOR,
        sender_company="Тест Отправитель",
        sender_phone="+79999999999",
        pickup_estimated_date=date.today(),
        pickup_time_from=time_from,
        pickup_time_to=time_to,
        sender_additional_info="Тестовая доп. информация",
        recipient_city=uuid4(),
        recipient_address="ул. Получательская, д.2",
        recipient_delivery_type=DeliveryType.DOOR,
        recipient_company="Тест Получатель",
        recipient_phone="+79998887766",
        delivery_estimated_date=date.today(),
        delivery_time_from=time_from,
        delivery_time_to=time_to,
        recipient_additional_info="Доп. инфа по получателю",
        weight=0.0,
        volume=0.0,
        places_count=0,
        created_by=seed_user,
        modified_by=seed_user,
    )
    return parcel


@pytest.fixture
async def seed_service(seed_user, seed_parcel):
    service = await Service.create(
        created_by=seed_user,
        modified_by=seed_user,
        parcel=seed_parcel,
        price_id=uuid4(),
        contract_id=uuid4(),
        service_type="standard",
        base_value=1,
    )
    return service
